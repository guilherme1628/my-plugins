"""
Data Formatters
Formatadores para diferentes tipos de dados de saída.
"""

import re
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional
try:
    from num2words import num2words
except ImportError:
    num2words = None


def format_field(value: str, field_type: str, format_spec: str = "") -> str:
    """
    Formata um campo baseado no tipo especificado.
    
    Args:
        value: Valor a ser formatado
        field_type: Tipo do campo
        format_spec: Especificação de formato adicional
        
    Returns:
        Valor formatado
    """
    if not value.strip():
        return ""
    
    formatters = {
        'text': format_text,
        'text_uppercase': format_text_uppercase,
        'date': format_date,
        'currency': format_currency,
        'currency_number': format_currency_number,
        'currency_text': format_currency_text,
        'email': format_email,
        'phone': format_phone,
        'number': format_number
    }
    
    formatter = formatters.get(field_type, format_text)
    return formatter(value, format_spec)


def format_text(value: str, format_spec: str = "") -> str:
    """Formata campo de texto."""
    formatted = value.strip()
    
    # Aplicar formatação específica baseada no format_spec
    if format_spec:
        if format_spec == "##.###.###/####-##":  # CNPJ
            formatted = format_cnpj(formatted)
        elif format_spec == "###.###.###-##":  # CPF
            formatted = format_cpf(formatted)
        elif format_spec == "#####-###" or format_spec == "##.###-###":  # CEP
            formatted = format_cep(formatted)
        elif "(" in format_spec and ")" in format_spec and "-" in format_spec:  # Telefone
            formatted = format_phone(formatted, format_spec)
        elif format_spec.lower() == "uppercase":
            formatted = formatted.upper()
        elif format_spec.lower() == "lowercase":
            formatted = formatted.lower()
        elif format_spec.lower() == "capitalize":
            formatted = formatted.capitalize()
        elif format_spec.lower() == "title":
            formatted = formatted.title()
    
    return formatted


def format_text_uppercase(value: str, format_spec: str = "") -> str:
    """Formata campo de texto convertendo para maiúsculas."""
    formatted = value.strip().upper()
    
    # Aplicar formatação específica se fornecida (após converter para maiúsculas)
    if format_spec:
        if format_spec == "##.###.###/####-##":  # CNPJ
            formatted = format_cnpj(formatted)
        elif format_spec == "###.###.###-##":  # CPF
            formatted = format_cpf(formatted)
        elif format_spec == "#####-###" or format_spec == "##.###-###":  # CEP
            formatted = format_cep(formatted)
        elif "(" in format_spec and ")" in format_spec and "-" in format_spec:  # Telefone
            formatted = format_phone(formatted, format_spec)
    
    return formatted


def format_date(value: str, format_spec: str = "dd/mm/yyyy") -> str:
    """Formata campo de data."""
    # Se já está no formato correto, retornar
    if format_spec == "dd/mm/yyyy" and re.match(r'\d{2}/\d{2}/\d{4}', value):
        return value
    
    # Tentar parsear diferentes formatos de entrada
    input_formats = ['%d/%m/%Y', '%d/%m/%y', '%d-%m-%Y', '%Y-%m-%d']
    parsed_date = None
    
    for fmt in input_formats:
        try:
            parsed_date = datetime.strptime(value, fmt)
            break
        except ValueError:
            continue
    
    # Formato extenso
    if not parsed_date:
        parsed_date = parse_extended_date(value)
    
    if not parsed_date:
        return value  # Retornar original se não conseguir parsear
    
    # Formatar conforme especificação
    output_formats = {
        'dd/mm/yyyy': '%d/%m/%Y',
        'dd/mm/yy': '%d/%m/%y',
        'dd-mm-yyyy': '%d-%m-%Y',
        'yyyy-mm-dd': '%Y-%m-%d',
        'dd de MMMM de yyyy': format_extended_date
    }
    
    output_format = output_formats.get(format_spec, '%d/%m/%Y')
    
    if callable(output_format):
        return output_format(parsed_date)
    else:
        return parsed_date.strftime(output_format)


def parse_extended_date(value: str) -> Optional[datetime]:
    """Converte data em formato extenso para datetime."""
    months = {
        'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4,
        'maio': 5, 'junho': 6, 'julho': 7, 'agosto': 8,
        'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12
    }
    
    pattern = r'(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})'
    match = re.match(pattern, value.lower().strip())
    
    if match:
        day, month_name, year = match.groups()
        if month_name in months:
            try:
                return datetime(int(year), months[month_name], int(day))
            except ValueError:
                pass
    
    return None


def format_extended_date(date_obj: datetime) -> str:
    """Formata datetime para formato extenso."""
    months = [
        'janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho',
        'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'
    ]
    
    day = date_obj.day
    month = months[date_obj.month - 1]
    year = date_obj.year
    
    return f"{day} de {month} de {year}"


def format_currency(value: str, format_spec: str = "R$ #.###,##") -> str:
    """Formata campo de valor monetário."""
    # Limpar entrada
    clean_value = value.replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
    
    try:
        amount = Decimal(clean_value)
        
        # Formatar conforme especificação
        if format_spec == "R$ #.###,##" or not format_spec:
            # Formato brasileiro padrão
            formatted = f"R$ {amount:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            return formatted
        elif format_spec == "#.###,##":
            # Sem símbolo de moeda
            formatted = f"{amount:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            return formatted
        elif format_spec == "####.##":
            # Formato americano
            return f"{amount:.2f}"
        else:
            # Formato padrão se não reconhecer
            formatted = f"R$ {amount:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            return formatted
            
    except Exception:
        return value


def format_currency_number(value: str, format_spec: str = "#.###,##") -> str:
    """Formata campo numérico sem símbolo de moeda."""
    # Limpar entrada
    clean_value = value.replace('R$', '').replace('$', '').replace(' ', '').replace('.', '').replace(',', '.')
    
    try:
        amount = Decimal(clean_value)
        
        # Formato brasileiro: ###.###,##
        formatted = f"{amount:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        return formatted
            
    except Exception:
        return value


def format_currency_text(value: str, format_spec: str = "") -> str:
    """Formata valor por extenso."""
    if not num2words:
        return value  # Se num2words não disponível, retornar original
    
    # Se o valor já é um número, converter para extenso
    try:
        # Tentar extrair número do valor
        clean_value = value.replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
        amount = float(clean_value)
        
        # Separar reais e centavos
        reais = int(amount)
        centavos = int((amount - reais) * 100)
        
        # Converter para extenso
        if reais == 0:
            reais_text = ""
        elif reais == 1:
            reais_text = "um real"
        else:
            reais_text = f"{num2words(reais, lang='pt_BR')} reais"
        
        if centavos == 0:
            centavos_text = ""
        elif centavos == 1:
            centavos_text = "um centavo"
        else:
            centavos_text = f"{num2words(centavos, lang='pt_BR')} centavos"
        
        # Combinar
        if reais_text and centavos_text:
            return f"{reais_text} e {centavos_text}"
        elif reais_text:
            return reais_text
        elif centavos_text:
            return centavos_text
        else:
            return "zero reais"
            
    except Exception:
        # Se não conseguir converter, retornar o valor original
        return value


def format_email(value: str, format_spec: str = "") -> str:
    """Formata campo de email."""
    return value.strip().lower()


def format_phone(value: str, format_spec: str = "(##) #####-####") -> str:
    """Formata campo de telefone."""
    # Remover formatação existente
    clean_phone = re.sub(r'[^\d]', '', value)
    
    # Aplicar formatação baseada no número de dígitos
    if len(clean_phone) == 10:
        # Telefone fixo: (11) 1234-5678
        return f"({clean_phone[:2]}) {clean_phone[2:6]}-{clean_phone[6:]}"
    elif len(clean_phone) == 11:
        # Celular: (11) 91234-5678
        return f"({clean_phone[:2]}) {clean_phone[2:7]}-{clean_phone[7:]}"
    else:
        return value  # Retornar original se formato inválido


def format_number(value: str, format_spec: str = "") -> str:
    """Formata campo numérico."""
    try:
        num = float(value.replace(',', '.'))
        
        if format_spec:
            # Se especificou formato, tentar aplicar
            if '.' in format_spec:
                decimals = len(format_spec.split('.')[1])
                return f"{num:.{decimals}f}"
        
        # Formato padrão - remover .0 desnecessário
        if num == int(num):
            return str(int(num))
        else:
            return f"{num:.2f}"
            
    except Exception:
        return value


def format_cnpj(cnpj: str) -> str:
    """Formata CNPJ para padrão XX.XXX.XXX/XXXX-XX."""
    clean_cnpj = re.sub(r'[^\d]', '', cnpj)
    
    if len(clean_cnpj) == 14:
        return f"{clean_cnpj[:2]}.{clean_cnpj[2:5]}.{clean_cnpj[5:8]}/{clean_cnpj[8:12]}-{clean_cnpj[12:]}"
    else:
        return cnpj


def format_cpf(cpf: str) -> str:
    """Formata CPF para padrão XXX.XXX.XXX-XX."""
    clean_cpf = re.sub(r'[^\d]', '', cpf)
    
    if len(clean_cpf) == 11:
        return f"{clean_cpf[:3]}.{clean_cpf[3:6]}.{clean_cpf[6:9]}-{clean_cpf[9:]}"
    else:
        return cpf


def format_cep(cep: str) -> str:
    """Formata CEP para padrão XXXXX-XXX."""
    clean_cep = re.sub(r'[^\d]', '', cep)
    
    if len(clean_cep) == 8:
        return f"{clean_cep[:5]}-{clean_cep[5:]}"
    else:
        return cep