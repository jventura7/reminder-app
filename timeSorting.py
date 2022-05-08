# String is in format:
# Input type: dict with x["Time"] in format -> year.month.day time hours.minute
# Note: Only works with military time
reminder1 = {"Title": "Dog food", "Time": "20.10.07 time 09.24", "message": "Buy extra food for Kyrie at PetCo"}
reminder2 = {"Title": "Take medicine", "Time": "21.10.07 time 13.05", "message": "Dont forget meds from Dr. Kurby"}
reminder3 = {"Title": "Daily Stretches", "Time": "20.10.07 time 12.05", "message": "Nightime exercise routine"}
allReminders = [reminder1, reminder2, reminder3]
allReminders.sort(key=lambda x: x["Time"])
print(allReminders)
