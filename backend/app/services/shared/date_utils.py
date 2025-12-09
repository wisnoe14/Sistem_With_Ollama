"""
Date Utilities Module
=====================

Provides date parsing, formatting, and conversion utilities for Indonesian language context.
Supports relative date expressions (besok, lusa, minggu depan), specific date patterns,
and Indonesian date formatting.

Features:
- Indonesian date formatting
- Relative date parsing (besok, lusa, minggu depan, etc.)
- Timeline expression detection
- Date pattern recognition (dd/mm, tanggal X)
- Current date information in Indonesian format

Author: Shared Utilities (Extracted from gpt_service)
"""

from datetime import datetime, timedelta
from typing import Dict
import re


def format_date_indonesian(date_obj: datetime) -> str:
    """
    Format tanggal dalam bahasa Indonesia
    
    Args:
        date_obj: datetime object to format
    
    Returns:
        String formatted date in Indonesian (e.g., "15 November 2025")
    
    Examples:
        >>> from datetime import datetime
        >>> format_date_indonesian(datetime(2025, 11, 15))
        '15 November 2025'
    """
    months_id = {
        1: "Januari", 2: "Februari", 3: "Maret", 4: "April",
        5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus", 
        9: "September", 10: "Oktober", 11: "November", 12: "Desember"
    }
    
    day = date_obj.day
    month = months_id[date_obj.month]
    year = date_obj.year
    
    return f"{day} {month} {year}"


def get_current_date_info() -> Dict:
    """
    Get informasi tanggal saat ini dalam berbagai format
    
    Returns:
        Dict containing:
        - tanggal_lengkap: Full date with day name (e.g., "Jumat, 15 November 2025")
        - tanggal: Date without day name (e.g., "15 November 2025")
        - hari: Day name (e.g., "Jumat")
        - bulan: Month name (e.g., "November")
        - tahun: Year number (e.g., 2025)
    
    Examples:
        >>> info = get_current_date_info()
        >>> print(info['tanggal'])
        '10 November 2025'
    """
    now = datetime.now()
    
    # Indonesian day names
    days_indonesian = {
        0: 'Senin', 1: 'Selasa', 2: 'Rabu', 3: 'Kamis',
        4: 'Jumat', 5: 'Sabtu', 6: 'Minggu'
    }
    
    # Indonesian month names
    months_indonesian = {
        1: 'Januari', 2: 'Februari', 3: 'Maret', 4: 'April', 5: 'Mei', 6: 'Juni',
        7: 'Juli', 8: 'Agustus', 9: 'September', 10: 'Oktober', 11: 'November', 12: 'Desember'
    }
    
    day_name = days_indonesian[now.weekday()]
    month_name = months_indonesian[now.month]
    
    return {
        "tanggal_lengkap": f"{day_name}, {now.day} {month_name} {now.year}",
        "tanggal": f"{now.day} {month_name} {now.year}",
        "hari": day_name,
        "bulan": month_name,
        "tahun": now.year
    }


def parse_time_expressions_to_date(text: str) -> Dict:
    """
    Konversi kata-kata waktu Indonesia menjadi tanggal spesifik
    
    Supports:
    - Relative expressions: besok, lusa, minggu depan, etc.
    - Number patterns: 3 hari, 2 minggu, 1 bulan
    - Day names: senin, selasa, rabu, etc.
    - Specific dates: tanggal 15, 20/11
    
    Args:
        text: Text containing time expression
    
    Returns:
        Dict containing:
        - original_text: Input text
        - detected_timeframe: Detected time expression
        - target_date: datetime object of target date
        - confidence: Confidence score (0-100)
        - formatted_date: Indonesian formatted date string
    
    Examples:
        >>> result = parse_time_expressions_to_date("besok saya bayar")
        >>> result['detected_timeframe']
        'besok'
        >>> result['confidence']
        85
    """
    now = datetime.now()
    text_lower = text.lower()
    
    result = {
        "original_text": text,
        "detected_timeframe": None,
        "target_date": None,
        "confidence": 0,
        "formatted_date": None
    }
    
    # Mapping kata waktu ke hari offset
    time_mappings = {
        # Hari-hari spesifik
        "besok": 1,
        "lusa": 2,
        "tulat": 3,
        "minggu depan": 7,
        "minggu ini": 3,
        
        # Frasa umum
        "hari ini": 0,
        "sekarang": 0,
        "sore ini": 0,
        "malam ini": 0,
        "pagi": 1,
        "siang": 0,
        "sore": 0,
        "malam": 0,
        
        # Periode waktu
        "1 hari": 1,
        "2 hari": 2,
        "3 hari": 3,
        "seminggu": 7,
        "dua minggu": 14,
        "sebulan": 30,
        
        # Spesifik hari
        "senin": None,  # Will be calculated
        "selasa": None,
        "rabu": None,
        "kamis": None,
        "jumat": None,
        "sabtu": None,
        "minggu": None
    }
    
    # Cek pattern angka + hari/minggu/bulan
    number_patterns = [
        (r'(\d+)\s*hari', 'days'),
        (r'(\d+)\s*minggu', 'weeks'),
        (r'(\d+)\s*bulan', 'months'),
        (r'dalam\s*(\d+)\s*hari', 'days'),
        (r'sekitar\s*(\d+)\s*hari', 'days')
    ]
    
    for pattern, unit in number_patterns:
        match = re.search(pattern, text_lower)
        if match:
            number = int(match.group(1))
            if unit == 'days':
                days_offset = number
            elif unit == 'weeks':
                days_offset = number * 7
            elif unit == 'months':
                days_offset = number * 30
                
            target_date = now + timedelta(days=days_offset)
            result.update({
                "detected_timeframe": f"{number} {unit}",
                "target_date": target_date,
                "confidence": 90,
                "formatted_date": format_date_indonesian(target_date)
            })
            return result
    
    # Cek kata-kata waktu umum
    for time_word, days_offset in time_mappings.items():
        if time_word in text_lower:
            if days_offset is not None:
                target_date = now + timedelta(days=days_offset)
                result.update({
                    "detected_timeframe": time_word,
                    "target_date": target_date,
                    "confidence": 85,
                    "formatted_date": format_date_indonesian(target_date)
                })
                return result
    
    # Cek hari dalam minggu (senin, selasa, dst)
    days_of_week = {
        "senin": 0, "selasa": 1, "rabu": 2, "kamis": 3, 
        "jumat": 4, "sabtu": 5, "minggu": 6
    }
    
    for day_name, day_num in days_of_week.items():
        if day_name in text_lower:
            current_weekday = now.weekday()
            days_ahead = day_num - current_weekday
            if days_ahead <= 0:  # Hari sudah lewat minggu ini
                days_ahead += 7
                
            target_date = now + timedelta(days=days_ahead)
            result.update({
                "detected_timeframe": f"{day_name} depan",
                "target_date": target_date,
                "confidence": 80,
                "formatted_date": format_date_indonesian(target_date)
            })
            return result
    
    # Cek pattern tanggal spesifik (dd/mm, dd-mm)
    date_patterns = [
        r'(\d{1,2})[/-](\d{1,2})',  # dd/mm atau dd-mm
        r'tanggal\s*(\d{1,2})',     # tanggal dd
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text_lower)
        if match:
            try:
                if len(match.groups()) == 2:
                    day, month = int(match.group(1)), int(match.group(2))
                else:
                    day = int(match.group(1))
                    month = now.month
                    
                target_date = datetime(now.year, month, day)
                if target_date <= now:
                    target_date = datetime(now.year + 1, month, day)
                    
                result.update({
                    "detected_timeframe": f"tanggal {day}/{month}",
                    "target_date": target_date,
                    "confidence": 95,
                    "formatted_date": format_date_indonesian(target_date)
                })
                return result
            except ValueError:
                continue
    
    return result


def parse_relative_date(text: str) -> Dict:
    """
    Parse relative date expressions and return actual dates
    
    Args:
        text: Text containing relative date expression
    
    Returns:
        Dict containing:
        - found: Boolean indicating if date was found
        - original_text: Matched expression
        - target_date: Date string in YYYY-MM-DD format
        - day_name: Indonesian day name
        - date_formatted: Indonesian formatted date
    
    Examples:
        >>> result = parse_relative_date("besok saya datang")
        >>> result['found']
        True
        >>> result['day_name']
        'Selasa'
    """
    today = datetime.now().date()
    text_lower = text.lower()
    
    days_indonesian = {
        0: 'senin', 1: 'selasa', 2: 'rabu', 3: 'kamis',
        4: 'jumat', 5: 'sabtu', 6: 'minggu'
    }
    
    months_indonesian = {
        1: 'januari', 2: 'februari', 3: 'maret', 4: 'april', 5: 'mei', 6: 'juni',
        7: 'juli', 8: 'agustus', 9: 'september', 10: 'oktober', 11: 'november', 12: 'desember'
    }
    
    date_expressions = {
        "hari ini": today,
        "besok": today + timedelta(days=1),
        "lusa": today + timedelta(days=2),
        "minggu depan": today + timedelta(weeks=1),
        "bulan depan": today.replace(month=today.month % 12 + 1) if today.month < 12 else today.replace(year=today.year + 1, month=1),
        "tahun depan": today.replace(year=today.year + 1)
    }
    
    # Add expressions for "X hari lagi" and "dalam X hari"
    for i in range(1, 31):
        date_expressions[f"{i} hari lagi"] = today + timedelta(days=i)
        date_expressions[f"dalam {i} hari"] = today + timedelta(days=i)
    
    for expression, target_date in date_expressions.items():
        if expression in text_lower:
            target_day_name = days_indonesian[target_date.weekday()]
            target_month_name = months_indonesian[target_date.month]
            
            return {
                "found": True,
                "original_text": expression,
                "target_date": target_date.strftime("%Y-%m-%d"),
                "day_name": target_day_name.title(),
                "date_formatted": f"{target_date.day} {target_month_name.title()} {target_date.year}"
            }
    
    return {
        "found": False,
        "original_text": "",
        "target_date": "",
        "day_name": "",
        "date_formatted": ""
    }


# Export public API
__all__ = [
    'format_date_indonesian',
    'get_current_date_info',
    'parse_time_expressions_to_date',
    'parse_relative_date',
]
