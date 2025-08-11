def detect_aoa_type(full_text):
    text_upper = full_text.upper()
    if "LIMITED BY GUARANTEE" in text_upper:
        return "private_guarantee"
    elif "PUBLIC COMPANY LIMITED BY SHARES" in text_upper:
        return "public_shares"
    elif "PRIVATE COMPANY LIMITED BY SHARES" in text_upper:
        return "private_shares"
    elif "SPECIAL PURPOSE VEHICLE" in text_upper:
        return "private_shares_spv"
    else:
        return None
