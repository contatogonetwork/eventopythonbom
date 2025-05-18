import datetime

def format_date(date):
    """Formata uma data para exibição"""
    if not date:
        return "-"
    
    if isinstance(date, str):
        try:
            date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            return date
    
    return date.strftime("%d/%m/%Y")

def format_datetime(dt):
    """Formata uma data e hora para exibição"""
    if not dt:
        return "-"
    
    if isinstance(dt, str):
        try:
            dt = datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            return dt
    
    return dt.strftime("%d/%m/%Y %H:%M")

def format_time(time):
    """Formata um horário para exibição"""
    if not time:
        return "-"
    
    if isinstance(time, str):
        try:
            time = datetime.datetime.strptime(time, "%H:%M").time()
        except ValueError:
            return time
    
    return time.strftime("%H:%M")

def get_date_range_string(start_date, end_date):
    """Retorna uma string formatada para um intervalo de datas"""
    if not start_date:
        return "-"
    
    if not end_date or start_date == end_date:
        return format_date(start_date)
    
    return f"{format_date(start_date)} a {format_date(end_date)}"