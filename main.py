from datetime import datetime
import time

from timetables import next_ferry_from_landungsbruecken, next_ferry_from_whb

# pegelnull zu seekartennull. unterschied 310cm
def to_marine_chart(measurement):
    return measurement - 310


if __name__ == '__main__':

    # todo integrate fahrplan
    # todo integrate twitter
    # todo integrate telegram

    #todo niedrigwasser?

    # todo warn if water levels in last day unusually high , verglichen mit MThw # get time of next hochwasser to estimate highpoint
    # sinus kurve mit normalpunkten und gezeitenzeiten
    # modellierung abweichung

    while True:
        current_info = get_current_info()

        print(current_info['measurement'])

        # get next departure time, get water_level prediction_at_time


        # todo integrate timetable to see if ferry is going later -> tide might fall
        if current_info['measurement'] > 420:
            print("the tide is too high")

        elif current_info['measurement'] > 410 and current_info['trend'] == 1:
            print("the tide is high and not falling")

        else:
            print('the ferry will go')

        # todo integrate timetable

        time.sleep(300)




