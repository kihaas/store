from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DecimalField, IntegerField, TextAreaField, URLField, SubmitField, BooleanField, validators
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange, Optional, ValidationError, Regexp
from website.models import User
import phonenumbers

# Валидатор для проверки международного формата телефонного номера
class PhoneNumberValidator:
    def __call__(self, form, field):
        try:
            number = phonenumbers.parse(field.data, None)  # None — не привязываем к конкретной стране
            if not phonenumbers.is_valid_number(number):
                raise ValueError
        except (phonenumbers.NumberParseException, ValueError):
            raise ValidationError('Введите корректный номер телефона в международном формате (например, +79123456789)')


class RegistrationForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()])
    email = StringField('Электронная почта', validators=[DataRequired(), Email()])
    phone = StringField('Телефон', validators=[
        DataRequired(),
        Regexp(r'\+?\d{10,15}$', message="Введите корректный номер телефона"),
        PhoneNumberValidator()
    ])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password', message='Пароли должны совпадать')])


class LoginForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()])
    email = StringField('Электронная почта', validators=[DataRequired(), Email()])
    phone = StringField('Телефон', validators=[
        DataRequired(),
        Regexp(r'\+?\d{10,15}$', message="Введите корректный номер телефона"),
        PhoneNumberValidator()
    ])
    password = PasswordField('Пароль', validators=[DataRequired()])

# Форма добавления/редактирования товара
class ProductForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    price = DecimalField('Цена', validators=[DataRequired(), NumberRange(min=0, message='Цена должна быть положительной')])
    description = TextAreaField('Описание', validators=[Optional()])
    stock = IntegerField('Количество на складе', validators=[DataRequired(), NumberRange(min=0, message='Количество не может быть отрицательным')])
    image_url = URLField('Ссылка на изображение', validators=[Optional()])
    submit = SubmitField('Сохранить')

# Форма обновления профиля пользователя
class UpdateProfileForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    login = StringField('Логин', validators=[DataRequired(), Length(min=3, max=20)])
    phone = StringField('Телефон', validators=[DataRequired(), PhoneNumberValidator()])
    current_password = PasswordField('Текущий пароль', validators=[DataRequired()])
    new_password = PasswordField('Новый пароль', validators=[Optional(), Length(min=8)])
    confirm_password = PasswordField('Подтвердите новый пароль', validators=[
        Optional(),
        EqualTo('new_password', message='Пароли должны совпадать')
    ])
    submit = SubmitField('Обновить профиль')

    def __init__(self, user_id, *args, **kwargs):
        super(UpdateProfileForm, self).__init__(*args, **kwargs)
        self.user_id = user_id

    def validate_login(self, login):
        user = User.query.filter_by(login=login.data).first()
        if user and user.id != self.user_id:
            raise ValidationError('Этот логин уже занят другим пользователем.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user and user.id != self.user_id:
            raise ValidationError('Этот email уже используется.')

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(message="Email обязателен"),
        Email(message="Некорректный формат email")
    ])

class ResetPasswordForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(message="Email обязателен"),
        Email(message="Некорректный формат email")
    ])
    code = StringField('Код подтверждения', validators=[
        DataRequired(message="Код подтверждения обязателен"),
        Length(min=6, max=6, message="Код должен состоять из 6 символов")
    ])
    new_password = PasswordField('Новый пароль', validators=[
        DataRequired(message="Новый пароль обязателен"),
        Length(min=8, message="Пароль должен быть не менее 8 символов")
    ])
    confirm_password = PasswordField('Подтвердите пароль', validators=[
        DataRequired(message="Подтверждение пароля обязательно"),
        EqualTo('new_password', message="Пароли должны совпадать")
    ])
