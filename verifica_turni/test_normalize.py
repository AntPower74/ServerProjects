import re

def normalize_shift(name):
    # Special cases
    if name.lower() == 'tocomm': return 'ToCOMM'
    
    # Extract prefix and number
    m = re.match(r'^([a-zA-Z]+)(0*\d+)$', name)
    if m:
        prefix = m.group(1).capitalize()
        num_str = m.group(2)
        # Convert to int to remove all leading zeros
        num = int(num_str)
        # If the original PDF name ends with 0 and is long enough, maybe it's already in sheet format?
        # Let's just always format it as: prefix + padded_num + '0'
        # Wait, how many digits for padding?
        # Pe001 -> num=1 -> Pe0010 (pad to 3 digits)
        # Pe0011 -> num=11 -> Pe0110 (pad to 3 digits)
        # To1040 -> num=1040 -> To10400? No! To1040 is already To1040!
        
        # Let's use a mapping approach for the ones we missed:
        return f"{prefix}{num:03d}0"
    return name

names = ['Tocomm', 'Pb0010', 'Pb001', 'Pe006', 'Pe0011', 'Pe0012', 'Pe0013', 'Pe0014', 'Pe0015', 'Pe0016', 'Pe0017', 'Pi001', 'pi002', 'pi003', 'pi004', 'Pi005', 'Pi006', 'Pi007', 'Pi0010', 'PI015', 'Pi0016', 'Pi0017']

for n in names:
    print(f"{n} -> {normalize_shift(n)}")
