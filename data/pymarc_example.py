import csv
from pymarc import Record, Field, MARCWriter

seed_data = [
    {
        "id": "SEED-2025-001",
        "common_name": "Bloodroot",
        "scientific_name": "Sanguinaria canadensis",
        "family": "Papaveraceae",
        "quantity": "Approx. 150 seeds",
        "lat": 38.9832,
        "lon": -76.8524,
        "date_collected": "YYYY-MM-DD",
        "date_packaged": "YYYY-MM-DD",
        "collection_event": "[collection event description]",
        "temperature_range": "15–25°C (59–77°F)",
        "germination": "Cold-moist stratification for 60 days before sowing",
        "usda_symbol": "SACA3",
        "usda_link": "https://plants.usda.gov/home/plantProfile?symbol=SACA3",
        "notes": "Woodland wildflower; early spring bloomer with white flowers.",
        "collector": "Mid-Atlantic Regional Seed Bank"
    },
    # ... (add remaining seed records here)
]

# MARC export
with open("native_seedbank_2025.mrc", "wb") as f:
    writer = MARCWriter(f)
    for item in seed_data:
        record = Record()
        record.add_field(Field(tag='001', data=item['id']))
        record.add_field(Field(tag='245', indicators=['1','0'], subfields=['a', f"{item['common_name']} /", 'b', item['scientific_name']]))
        record.add_field(Field(tag='260', indicators=['\\','\\'], subfields=['c', '2025']))
        record.add_field(Field(tag='300', indicators=['\\','\\'], subfields=['a', item['quantity']]))
        record.add_field(Field(tag='500', indicators=['\\','\\'], subfields=['a', f"Family: {item['family']}"]))
        record.add_field(Field(tag='500', indicators=['\\','\\'], subfields=['a', f"Growing temperature range: {item['temperature_range']}"]))
        record.add_field(Field(tag='500', indicators=['\\','\\'], subfields=['a', f"Germination requirements: {item['germination']}"]))
        record.add_field(Field(tag='518', indicators=['\\','\\'], subfields=['a', f"Collected {item['date_collected']} during {item['collection_event']}"]))
        record.add_field(Field(tag='583', indicators=['\\','\\'], subfields=['a', f"Packaged {item['date_packaged']}"]))
        record.add_field(Field(tag='034', indicators=['0','\\'], subfields=['d', str(item['lon']), 'f', str(item['lat'])]))
        record.add_field(Field(tag='024', indicators=['7','\\'], subfields=['a', item['usda_symbol'], '2', 'USDA-PLANTS']))
        record.add_field(Field(tag='856', indicators=['4','0'], subfields=['u', item['usda_link']]))
        record.add_field(Field(tag='710', indicators=['2','\\'], subfields=['a', item['collector']]))
        record.add_field(Field(tag='500', indicators=['\\','\\'], subfields=['a', item['notes']]))
        writer.write(record)
        
