"""
Data Validators
Validadores para diferentes tipos de campos de entrada.
"""

import re
from datetime import datetime
from typing import Any, Optional
from decimal import Decimal, InvalidOperation


class ValidationError(Exception):
    """Erro de validação de campo."""
    pass


def validate_field(value: str, field_type: str, format_spec: str = "", optional: bool = False) -> bool:
    """
    Valida um campo baseado no tipo especificado.
    
    Args:
        value: Valor a ser validado
        field_type: Tipo do campo (text, date, currency, etc.)
        format_spec: Especificação de formato adicional
        optional: Se o campo é opcional
        
    Returns:
        True se válido
        
    Raises:
        ValidationError: Se inválido com mensagem explicativa
    """
    # Campos opcionais podem ficar vazios
    if optional and not value.strip():
        return True
    
    # Campos obrigatórios não podem ficar vazios
    if not optional and not value.strip():
        raise ValidationError("Campo obrigatório não pode ficar vazio")
    
    # Chamar validador específico por tipo
    validators = {
        'text': validate_text,
        'text_uppercase': validate_text,  # Mesma validação que text
        'date': validate_date,
        'currency': validate_currency,
        'currency_number': validate_currency_number,
        'currency_text': validate_currency_text,
        'email': validate_email,
        'phone': validate_phone,
        'number': validate_number
    }
    
    validator = validators.get(field_type, validate_text)
    return validator(value, format_spec)


def validate_text(value: str, format_spec: str = "") -> bool:
    """Valida campo de texto."""
    if len(value.strip()) == 0:
        raise ValidationError("Texto não pode estar vazio")
    
    # Validações específicas baseadas no format_spec
    if format_spec:
        if format_spec == "##.###.###/####-##":  # CNPJ
            return validate_cnpj(value)
        elif format_spec == "###.###.###-##":  # CPF
            return validate_cpf(value)
        elif format_spec == "#####-###" or format_spec == "##.###-###":  # CEP
            # Validar formato básico de CEP
            clean_cep = re.sub(r'[^\d]', '', value)
            if len(clean_cep) != 8:
                raise ValidationError("CEP deve ter 8 dígitos")
        elif "(" in format_spec and ")" in format_spec and "-" in format_spec:  # Telefone
            return validate_phone(value, format_spec)
        elif format_spec.isdigit():
            # Validar tamanho máximo se especificado como número
            max_length = int(format_spec)
            if len(value) > max_length:
                raise ValidationError(f"Texto não pode ter mais de {max_length} caracteres")
    
    return True


def validate_date(value: str, format_spec: str = "dd/mm/yyyy") -> bool:
    """Valida campo de data."""
    # Formatos suportados
    date_formats = {
        'dd/mm/yyyy': '%d/%m/%Y',
        'dd/mm/yy': '%d/%m/%y',
        'dd-mm-yyyy': '%d-%m-%Y',
        'yyyy-mm-dd': '%Y-%m-%d',
        'dd de MMMM de yyyy': None  # Formato extenso - tratamento especial
    }
    
    if not format_spec:
        format_spec = 'dd/mm/yyyy'
    
    python_format = date_formats.get(format_spec, '%d/%m/%Y')
    
    if python_format:
        try:
            datetime.strptime(value, python_format)
            return True
        except ValueError:
            raise ValidationError(f"Data inválida. Use o formato: {format_spec}")
    else:
        # Formato extenso - validação mais flexível
        if validate_extended_date(value):
            return True
        else:
            raise ValidationError(f"Data inválida. Use o formato: {format_spec}")


def validate_extended_date(value: str) -> bool:
    """Valida data em formato extenso como '15 de janeiro de 2025'."""
    months = {
        'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4,
        'maio': 5, 'junho': 6, 'julho': 7, 'agosto': 8,
        'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12
    }
    
    # Regex para formato "dd de mês de yyyy"
    pattern = r'(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})'
    match = re.match(pattern, value.lower().strip())
    
    if not match:
        return False
    
    day, month_name, year = match.groups()
    
    if month_name not in months:
        return False
    
    try:
        # Verificar se é uma data válida
        datetime(int(year), months[month_name], int(day))
        return True
    except ValueError:
        return False


def validate_currency(value: str, format_spec: str = "R$ #.###,##") -> bool:
    """Valida campo de valor monetário."""
    # Remover formatação comum
    clean_value = value.replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
    
    try:
        amount = Decimal(clean_value)
        if amount < 0:
            raise ValidationError("Valor monetário não pode ser negativo")
        return True
    except InvalidOperation:
        raise ValidationError("Valor monetário inválido. Use formato: R$ 1.234,56 ou 1234.56")


def validate_currency_number(value: str, format_spec: str = "#.###,##") -> bool:
    """Valida campo numérico (sem símbolo de moeda)."""
    # Remover formatação comum (incluindo símbolos de moeda)
    clean_value = value.replace('R$', '').replace('$', '').replace(' ', '').replace('.', '').replace(',', '.')
    
    try:
        amount = Decimal(clean_value)
        if amount < 0:
            raise ValidationError("Valor não pode ser negativo")
        return True
    except InvalidOperation:
        raise ValidationError("Valor numérico inválido. Use formato: 1.234,56 ou 1234.56")


def validate_currency_text(value: str, format_spec: str = "") -> bool:
    """Valida campo de valor por extenso."""
    # Para valores por extenso, aceitar qualquer texto não vazio
    # A conversão será feita pelo formatter
    if len(value.strip()) == 0:
        raise ValidationError("Valor por extenso não pode estar vazio")
    return True


def validate_email(value: str, format_spec: str = "") -> bool:
    """Valida campo de email."""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, value):
        raise ValidationError("Email inválido. Use formato: usuario@dominio.com")
    
    return True


def validate_phone(value: str, format_spec: str = "(##) #####-####") -> bool:
    """Valida campo de telefone."""
    # Remover formatação
    clean_phone = re.sub(r'[^\d]', '', value)
    
    # Verificar tamanho (10 ou 11 dígitos para Brasil)
    if len(clean_phone) not in [10, 11]:
        raise ValidationError("Telefone deve ter 10 ou 11 dígitos")
    
    # Verificar se começa com DDD válido
    if len(clean_phone) >= 2:
        ddd = int(clean_phone[:2])
        valid_ddds = list(range(11, 100))  # DDDs válidos no Brasil
        if ddd not in valid_ddds or ddd < 11:
            raise ValidationError("DDD inválido")
    
    return True


def validate_number(value: str, format_spec: str = "") -> bool:
    """Valida campo numérico."""
    try:
        float(value.replace(',', '.'))
        return True
    except ValueError:
        raise ValidationError("Número inválido")


def validate_cnpj(cnpj: str) -> bool:
    """Valida CNPJ brasileiro."""
    # Remover formatação
    cnpj = re.sub(r'[^\d]', '', cnpj)
    
    # Verificar tamanho
    if len(cnpj) != 14:
        raise ValidationError("CNPJ deve ter 14 dígitos")
    
    # Verificar se não são todos iguais
    if cnpj == cnpj[0] * 14:
        raise ValidationError("CNPJ inválido")
    
    # Algoritmo de validação do CNPJ
    def calculate_digit(cnpj_partial, weights):
        sum_result = sum(int(digit) * weight for digit, weight in zip(cnpj_partial, weights))
        remainder = sum_result % 11
        return 0 if remainder < 2 else 11 - remainder
    
    weights1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    weights2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    
    first_digit = calculate_digit(cnpj[:12], weights1)
    second_digit = calculate_digit(cnpj[:13], weights2)
    
    if int(cnpj[12]) != first_digit or int(cnpj[13]) != second_digit:
        raise ValidationError("CNPJ inválido")
    
    return True


def validate_cpf(cpf: str) -> bool:
    """Valida CPF brasileiro."""
    # Remover formatação
    cpf = re.sub(r'[^\d]', '', cpf)
    
    # Verificar tamanho
    if len(cpf) != 11:
        raise ValidationError("CPF deve ter 11 dígitos")
    
    # Verificar se não são todos iguais
    if cpf == cpf[0] * 11:
        raise ValidationError("CPF inválido")
    
    # Algoritmo de validação do CPF
    def calculate_digit(cpf_partial, weights):
        sum_result = sum(int(digit) * weight for digit, weight in zip(cpf_partial, weights))
        remainder = sum_result % 11
        return 0 if remainder < 2 else 11 - remainder
    
    weights1 = list(range(10, 1, -1))
    weights2 = list(range(11, 1, -1))
    
    first_digit = calculate_digit(cpf[:9], weights1)
    second_digit = calculate_digit(cpf[:10], weights2)
    
    if int(cpf[9]) != first_digit or int(cpf[10]) != second_digit:
        raise ValidationError("CPF inválido")
    
    return True