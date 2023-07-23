# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import Restarted,SlotSet,EventType
import webbrowser
import pymongo
from datetime import datetime

from rasa_sdk.interfaces import Tracker
from rasa_sdk.types import DomainDict

current_time = datetime.now()
client = pymongo.MongoClient("mongodb://localhost:27017")
db= client["EventBuzz"]
coll=db["Event List"]

class ActionVideo(Action):
    def name(self) -> Text:
        return "action_video"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) -> List[Dict[Text, Any]]:
        video_url = "https://youtu.be/qsZTVMzQRo0"
        dispatcher.utter_message("wait, playing your video.")
        webbrowser.open(video_url)
        return []
    
class ActionMNNITSITE1(Action):
    def name(self) -> Text:
        return "take_me_to_home"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) -> List[Dict[Text, Any]]:
        site_url = "mnnit.ac.in"
        dispatcher.utter_message(site_url)
        # webbrowser.open(site_url)
        return []
    
class ActionMNNITSITE2(Action):
    def name(self) -> Text:
        return "take_me_to_academic"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) -> List[Dict[Text, Any]]:
        site_url = "https://academics.mnnit.ac.in/new"
        dispatcher.utter_message("wait, the site is opening")
        webbrowser.open(site_url)
        return []

class ConvoRestart(Action):
    def name(self) -> Text:
        return "restart_convo"
    def run(self, dispatcher:CollectingDispatcher, tracker:Tracker, domain: Dict[Text,Any]) -> List[Dict[Text,Any]]:
        return[Restarted()]
    
class say_events_(Action):

    def name(self) -> Text:
         return "action_say_events"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        found = coll.find_one({"EventDate":{"$gt":current_time}}, {"_id":0})
        event_name = found["EventName"]
        event_type = found["EventType"]
        event_start= found["StartTime"] 
        event_end = found["EndTime"]
        event_date = found["EventDate"]
        desired_format = "%Y-%m-%d"
        parsed_datetime = event_date.strftime(desired_format)
        datetime_object = datetime.strptime(parsed_datetime, "%Y-%m-%d")
        day_of_week_number = datetime_object.weekday()
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        message = "The next event in the college is "+event_name+". It is a "+event_type+" event, from "+event_start+" to "+event_end+" on "+parsed_datetime+"("+days[day_of_week_number]+")"
        if not found == None:
            dispatcher.utter_message(text=message)
        else:
            message = "No important events are going to be hosted."
        dispatcher.utter_message(text=message)
        return []

class say_events_month(Action):

    def name(self) -> Text:
         return "action_say_mevents"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        entities = tracker.latest_message.get('entities', [])
        month_entity = next((entity for entity in entities if entity['entity'] == 'month_name'), None)
        months=["january","february","march","april","may","june","july","august","september","october","november","december"]
        month_value = str(month_entity['value'])
        userin=month_value.lower()
        index=0
        for i in range(0,12):
            if(userin==months[i]):
                index=i+1
                break
        years=current_time.year

        index1 = str(years)+"-"+str(index)+"-01"
        index2 = str(years)+"-"+str(index)+"-31"
        month_date_open = datetime.strptime(index1, "%Y-%m-%d")
        month_date_end = datetime.strptime(index2, "%Y-%m-%d")
        found = coll.find_one({"EventDate":{"$gte":month_date_open,"$lte":month_date_end}}, {"_id":0})
        if found:
            event_name = found["EventName"]
            event_type = found["EventType"]
            event_start= found["StartTime"] 
            event_end = found["EndTime"]
            event_date = found["EventDate"]
            desired_format = "%Y-%m-%d"
            parsed_datetime = event_date.strftime(desired_format)
            datetime_object = datetime.strptime(parsed_datetime, "%Y-%m-%d")
            day_of_week_number = datetime_object.weekday()
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            message = "Yes, there is an event in that month. The event is "+event_name+". It is a "+event_type+" event, from "+event_start+" to "+event_end+" on "+parsed_datetime+"("+days[day_of_week_number]+")"
        else:
            message = "No important events are going to be hosted in that month"
        dispatcher.utter_message(text=message)
        return []
    

class ValidateForm(Action):
    def name(self) -> Text:
        return "user_details_form"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[EventType]:
        required_slots = ["name","number","regno"]

        for slot_name in required_slots:
            if tracker.slots.get(slot_name) is None:
                # The slot is not filled yet, request the user to fill the slot
                return [SlotSet("requested_slot",slot_name)]
            # All slots are filled.
            return [SlotSet("requested_slot",None)]

class ActionSubmit(Action):
    def name(self) -> Text:
        return "action_submit"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(template="utter_details_thanks",Name=tracker.get_slot("name"),Mobile_number=tracker.get_slot("number"),Registration_No=tracker.get_slot("regno"))