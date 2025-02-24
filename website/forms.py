from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DecimalField, IntegerField, TextAreaField, URLField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange, Optional, ValidationError
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
            raise ValidationError('Введите корректный номер телефона в международном формате (например, +1234567890)')

# Форма регистрации нового пользователя
class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    login = StringField('Логин', validators=[DataRequired(), Length(min=3, max=20)])
    phone = StringField('Телефон', validators=[DataRequired(), PhoneNumberValidator()])
    password = PasswordField('Пароль', validators=[
        DataRequired(),
        Length(min=8, message='Пароль должен содержать не менее 8 символов')
    ])
    confirm_password = PasswordField('Подтвердите пароль', validators=[
        DataRequired(), EqualTo('password', message='Пароли должны совпадать')
    ])
    referral_code = StringField('Реферальный код', validators=[Optional()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Зарегистрироваться')

    def validate_login(self, login):
        user = User.query.filter_by(login=login.data).first()
        if user:
            raise ValidationError('Этот логин уже используется. Пожалуйста, выберите другой.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Этот email уже зарегистрирован.')

    def validate_referral_code(self, referral_code):
        if referral_code.data:
            referrer = User.query.filter_by(referral_code=referral_code.data).first()
            if not referrer:
                raise ValidationError('Неверный реферальный код.')

# Форма авторизации пользователя
class LoginForm(FlaskForm):
    email_or_login = StringField('Email или Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')

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
    password = PasswordField('Новый пароль', validators=[Optional(), Length(min=8)])
    confirm_password = PasswordField('Подтвердите новый пароль', validators=[EqualTo('password', message='Пароли должны совпадать')])
    submit = SubmitField('Обновить профиль')

    def validate_login(self, login):
        user = User.query.filter_by(login=login.data).first()
        if user and user.id != self._obj.id:  # Позволяем текущему пользователю обновлять свои данные
            raise ValidationError('Этот логин уже занят другим пользователем.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user and user.id != self._obj.id:
            raise ValidationError('Этот email уже используется.')
