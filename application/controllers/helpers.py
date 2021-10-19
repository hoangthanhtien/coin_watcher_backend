import datetime
import uuid  # import decimal
import datetime
from sqlalchemy.ext import hybrid
from sqlalchemy.orm.query import Query
from sqlalchemy.exc import NoInspectionAvailable
from sqlalchemy.ext.associationproxy import AssociationProxy
from sqlalchemy.orm import RelationshipProperty as RelProperty
from sqlalchemy.inspection import inspect as sqlalchemy_inspect
from string import Template
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from application.config import Config
from application.models.model import User
from application.database import db, redis_db
import requests

# from sanic.response import json
import json
from application.controllers import generate_random_string
import time

COLUMN_BLACKLIST = ("_sa_polymorphic_on",)


def timestamp_to_datetime(timestamp):
    timestamp = datetime.datetime.fromtimestamp(timestamp)
    return str(timestamp.strftime("%d-%m-%Y %H:%M:%S"))


def timestamp_to_date(timestamp):
    dt_obj = datetime.datetime.fromtimestamp(timestamp).strftime("%d-%m-%Y")
    return str(dt_obj)


def get_current_timestamp():
    ts = datetime.datetime.now().timestamp()
    return int(ts)


def convert_datestring_to_timestamp(date):
    result = time.mktime(datetime.datetime.strptime(date, "%d-%m-%Y").timetuple())
    return int(result)


def is_mapped_class(cls):
    try:
        sqlalchemy_inspect(cls)
        return True
    except Exception as e:
        print("Exception: ", e)
        return False


def is_like_list(instance, relation):
    """Returns ``True`` if and only if the relation of `instance` whose name is
    `relation` is list-like.

    A relation may be like a list if, for example, it is a non-lazy one-to-many
    relation, or it is a dynamically loaded one-to-many.

    """
    if relation in instance._sa_class_manager:
        return instance._sa_class_manager[relation].property.uselist
    elif hasattr(instance, relation):
        attr = getattr(instance._sa_instance_state.class_, relation)
        if hasattr(attr, "property"):
            return attr.property.uselist
    related_value = getattr(type(instance), relation, None)
    if isinstance(related_value, AssociationProxy):
        local_prop = related_value.local_attr.prop
        if isinstance(local_prop, RelProperty):
            return local_prop.uselist
    return False


def to_dict(
    instance,
    deep=None,
    exclude=None,
    include=None,
    exclude_relations=None,
    include_relations=None,
    include_methods=None,
):
    if (exclude is not None or exclude_relations is not None) and (
        include is not None or include_relations is not None
    ):
        raise ValueError("Cannot specify both include and exclude.")
    # Create a list of names of columns, including hybrid properties
    instance_type = type(instance)
    try:
        inspected_instance = sqlalchemy_inspect(instance_type)
        column_attrs = inspected_instance.column_attrs.keys()
        descriptors = inspected_instance.all_orm_descriptors.items()
        hybrid_columns = [
            k
            for k, d in descriptors
            if d.extension_type == hybrid.HYBRID_PROPERTY and not (deep and k in deep)
        ]
        columns = column_attrs + hybrid_columns
    except NoInspectionAvailable:
        return instance
    # Filter the columns based on exclude and include values
    if exclude is not None:
        columns = (c for c in columns if c not in exclude)
    elif include is not None:
        columns = (c for c in columns if c in include)
    # Create a dictionary mapping column name to value
    result = dict(
        (col, getattr(instance, col))
        for col in columns
        if not (col.startswith("__") or col in COLUMN_BLACKLIST)
    )
    # Add any included methods
    if include_methods is not None:
        for method in include_methods:
            if "." not in method:
                value = getattr(instance, method)
                # Allow properties and static attributes in include_methods
                if callable(value):
                    value = value()
                result[method] = value
    # Check for objects in the dictionary that may not be serializable by default.
    # Convert datetime objects to ISO 8601 format, convert UUID objects to hexadecimal strings, etc.
    for key, value in result.items():
        if isinstance(value, (datetime.date, datetime.time)):
            result[key] = value.isoformat()
        elif isinstance(value, uuid.UUID):
            result[key] = str(value)
        # elif isinstance(value, decimal.Decimal):
        #     result[key] = float(value)
        elif key not in column_attrs and is_mapped_class(type(value)):
            result[key] = to_dict(value)
    # Recursively call _to_dict on each of the `deep` relations
    deep = deep or {}
    for relation, rdeep in deep.items():
        # Get the related value so we can see if it is None, a list, a query (as specified by a dynamic relationship loader), or an actual
        # instance of a model.
        relatedvalue = getattr(instance, relation)
        if relatedvalue is None:
            result[relation] = None
            continue
        # Determine the included and excluded fields for the related model.
        newexclude = None
        newinclude = None
        if exclude_relations is not None and relation in exclude_relations:
            newexclude = exclude_relations[relation]
        elif include_relations is not None and relation in include_relations:
            newinclude = include_relations[relation]
        # Determine the included methods for the related model.
        newmethods = None
        if include_methods is not None:
            newmethods = [
                method.split(".", 1)[1]
                for method in include_methods
                if method.split(".", 1)[0] == relation
            ]
        if is_like_list(instance, relation):
            result[relation] = [
                to_dict(
                    inst,
                    rdeep,
                    exclude=newexclude,
                    include=newinclude,
                    include_methods=newmethods,
                )
                for inst in relatedvalue
            ]
            continue
        # If the related value is dynamically loaded, resolve the query to get the single instance.
        if isinstance(relatedvalue, Query):
            relatedvalue = relatedvalue.one()
        result[relation] = to_dict(
            relatedvalue,
            rdeep,
            exclude=newexclude,
            include=newinclude,
            include_methods=newmethods,
        )

    return result


async def read_template(filename: str):
    with open(filename, "r", encoding="utf-8") as template_file:
        template_file_content = template_file.read()
    return Template(template_file_content)


async def get_user_fullname(email: str):
    user_record = db.session.query(User).filter(User.email == email).first()
    if not user_record:
        return None
    return user_record.full_name if user_record.full_name else None


async def get_user_info(email: str):
    user_record = db.session.query(User).filter(User.email == email).first()
    return to_dict(user_record) if user_record else None


async def create_validate_string(email):
    validate_string = generate_random_string(length=64, type="letters")
    key_existed = redis_db.get(validate_string)
    # user_info = await get_user_info(email)
    while key_existed:
        validate_string = generate_random_string(length=64, type="letters")
        key_existed = redis_db.get(validate_string)
    redis_db.set(validate_string)
    return validate_string


def send_chatbot_noti(message: str = None):
    params = {
        "verify_token": Config.CHAT_BOT_VERIFY_TOKEN,
        "message": message,
    }
    requests.post(Config.CHAT_BOT_WEBHOOKS, params=params)
    return True


async def send_email(
    to_email_addresses: list, mail_content_type: str, additional_data=None
):
    """Gửi email
    :param list to_email_addresses: Mảng địa chỉ người nhận mail
    :param str mail_content_type: Loại nội dung gửi đi, bao gồm - welcome : Mail chào mừng
        - send_validate_code : Mail gửi mã code bí mật dùng để reset mật khẩu hoặc kích hoạt account
        - validate_success : Thông báo validate thành công
        - notify_price : Thông báo giá của crypto currency
    :param any additional_data: Thông tin đính kèm
    """
    # try:
    # set up the SMTP server
    print("Đang gửi email")
    s = smtplib.SMTP(host="smtp.gmail.com", port=587)
    s.starttls()
    s.login(Config.SENDER_ACCOUNT, Config.SENDER_ACCOUNT_PASSWORD)
    # if not mail_content_type:
    #     return json(Config.SERVER_ERROR, 500)
    if mail_content_type == "welcome":
        message_template = await read_template(filename=Config.WELCOME_MAIL_TEMPLATE)
        email_header = Config.WELCOME_MAIL_HEADER
    if mail_content_type == "send_validate_code":
        message_template = await read_template(filename=Config.VALIDATE_MAIL_TEMPLATE)
        email_header = Config.VALIDATE_MAIL_HEADER
    if mail_content_type == "notify_price":
        message_template = await read_template(
            filename=Config.NOTIFY_PRICE_MAIL_TEMPLATE
        )
        email_header = Config.NOTIFY_PRICE_MAIL_HEADER

    for email_address in to_email_addresses:
        msg = MIMEMultipart()
        user_full_name = await get_user_fullname(email=email_address)
        # user_full_name = "Hoàng Thành Tiến"
        if mail_content_type == "welcome":
            message = message_template.substitute(PERSON_NAME=user_full_name)
        if mail_content_type == "notify_price":
            message = message_template.substitute(
                PERSON_NAME=user_full_name,
                COIN_ID=additional_data.get("coin_id"),
                PRICE=additional_data.get("price"),
            )
        if mail_content_type == "send_validate_code":
            pass

        msg["From"] = Config.SENDER_ACCOUNT
        msg["To"] = email_address
        msg["Subject"] = email_header
        msg.attach(MIMEText(message, "plain"))

        s.send_message(msg)
        print("Da gui email")
        del msg
    # except Exception:
    #     return json(Config.SEND_EMAIL_ERR,500)
    return True
