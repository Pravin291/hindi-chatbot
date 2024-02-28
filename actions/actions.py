

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import AllSlotsReset,Restarted
import datetime


# database connectivity

import mysql.connector

db_config = {
   
}

# Establish a connection to the database
conn = mysql.connector.connect(**db_config)

# connectivity finished

my_dict={}
class ActionAddItemToOrder(Action):
      def name(self):
            return "action_add_items_to_order"

      def run(self, dispatcher, tracker, domain):
       
     

            entities = tracker.latest_message['entities']
           
            store_entity_name=[]
            store_entity_value=[]

            if len(entities)!=0:
                  
                  
                  for ent in entities:
                        
                        if  ent["entity"]=="food_item" :
                              store_entity_name.append(ent["value"])
                        else :
                              store_entity_value.append(int(ent["value"]))
                    
                       
                  if len(store_entity_value)==len(store_entity_name):
                        for i in range(len(store_entity_name)):
                              my_dict.setdefault(store_entity_name[i], 0)
                              my_dict[store_entity_name[i]]+=store_entity_value[i]
                              # print(str(store_entity_value[i])+" "+ store_entity_name[i]+" added")

                        dispatcher.utter_message("और कुछ ")
                        

                  else :
                        store_entity_name.clear()
                        store_entity_value.clear()
                        dispatcher.utter_message("मैं समझ नहीं पाया कृपया व्यंजन(खाने का पदार्थ) और संख्या की जाँच करे")

            else:
                  
                  dispatcher.utter_message("No entities were mentioned in your message.")

            
            
            return []



class OrderCheckout(Action):
      def name(self):
            return "action_order_checkout"

      def run(self, dispatcher, tracker, domain):
      

            dispatcher.utter_message("ये रहा आपका आर्डर :\n")
            for key,value in my_dict.items():
               dispatcher.utter_message(key+" "+str(value))
               print(type(key) , type(value))
            
            dispatcher.utter_message("आर्डर प्लेस करने के लिए हाँ लिखे अथवा [व्यंजन] [संख्या] कम करो या जोड़ दो लिखे \n")
            return []


class removeItemsFromOrder(Action):
      def name(self):
            return "action_remove_items_from_order"

      def run(self, dispatcher, tracker, domain):

            entities = tracker.latest_message['entities']
           
            store_entity_name=[]
            store_entity_value=[]

            if len(entities)!=0:
                  
                  
                  for ent in entities:
                        
                        if  ent["entity"]=="food_item" :
                              store_entity_name.append(ent["value"])
                        else :
                              store_entity_value.append(int(ent["value"]))
                    
                       
                  cnt=0
                  remove=0
                  if len(store_entity_value)==len(store_entity_name):
                        for i in range(len(store_entity_name)):
                              
                              
                              if(store_entity_value[i] <= my_dict[store_entity_name[i]]):
                                    my_dict[store_entity_name[i]]-=store_entity_value[i]

                                    if(my_dict[store_entity_name[i]]==0):
                                          my_dict.pop(store_entity_name[i])
                                          
                                    dispatcher.utter_message(str(store_entity_value[i])+" "+store_entity_name[i]+" निकाले गए"+"\n")
                                    
                              else:
                                    cnt=1
                                    remove=my_dict[store_entity_name[i]]
                                    break

                        if cnt==1:
                              dispatcher.utter_message("माफ़ कीजिये गा पर आप " + str(remove)+ " से ज्यादा नहीं निकाल सकते \n")
                        
                        else: 
                              
                              dispatcher.utter_message("और कुछ ")
                        
                        

                  else :
                        store_entity_name.clear()
                        store_entity_value.clear()
                        dispatcher.utter_message("मैं समझ नहीं पाया कृपया व्यंजन(खाने का पदार्थ) और संख्या की जाँच करे \n")
            else:
                  dispatcher.utter_message("मैं समझ नहीं पाया कृपया व्यंजन(खाने का पदार्थ) और संख्या की जाँच करे \n")
                 
            
            return []

class OrderFinish(Action):
    def name(self):
        return "action_order_finish"

    def run(self, dispatcher, tracker, domain):

        if len(my_dict) == 0:
            dispatcher.utter_message("माफ़ कीजियेगा पर बिना कुछ आर्डर किये आप आर्डर प्लेस नहीं कर सकते")
            return []

        cursor = conn.cursor()
        query = "SELECT MAX(order_id) FROM orders"
        cursor.execute(query)
        result = cursor.fetchone()

        if result is not None:
            newOrderId = result[0] + 1  # start the new order
        else:
            newOrderId = 1

        for key, value in my_dict.items():

            quantity = value

            query1 = "SELECT food_id FROM food_items WHERE food_item_name = %s"
            query2 = "SELECT price FROM food_items WHERE food_item_name = %s"

            cursor.execute(query1, (key,))  # get the item_id of ordered food
            result_item = cursor.fetchone()

            if result_item is not None:
                item_ID = result_item[0]
            else:
                item_ID = None

            cursor.execute(query2, (key,))  # get the price of ordered_food
            result_price = cursor.fetchone()

            if result_price is not None:
                price = result_price[0]
            else:
                price = None

            if item_ID is not None and price is not None:
                insert_query = "INSERT INTO ordered_items (order_id, food_id, quantity,price) VALUES (%s, %s, %s,%s)"
                data = (newOrderId, item_ID, quantity, price * quantity)

                cursor.execute(insert_query, data)
                conn.commit()  # to store in ordered_items table

        # calculate the total price
        query4 = "SELECT SUM(price) FROM ordered_items where order_id=%s"
        cursor.execute(query4, (newOrderId,))
        result_sum = cursor.fetchone()

        if result_sum is not None:
            sum = result_sum[0]
        else:
            sum = None

        # also store in orders table
        query3 = "INSERT INTO orders (order_id,date,total_price) VALUES (%s,%s,%s)"
        date = datetime.date.today()
        data1 = (newOrderId, date, sum)
        cursor.execute(query3, data1)

        # store the order in track table
        query5 = "INSERT INTO order_tracking (order_id,status) VALUES (%s,%s)"
        data2 = (newOrderId, "pending")
        cursor.execute(query5, data2)

        conn.commit()  # store in orders table
        cursor.close()

        dispatcher.utter_message("आपका आर्डर पूरा हो गया है \n ")
        dispatcher.utter_message("आपके आर्डर की कुल कीमत :रु " + str(sum))
        dispatcher.utter_message("आपकी आर्डर ID : " + str(newOrderId))
        dispatcher.utter_message("आर्डर ट्रैक करने के लिए ट्रैक [आर्डर ID] लिखे ")
        dispatcher.utter_message("आपक ओर्डर दर्ज कर दिया गया , आर्डर करने के लिए धन्यवाद")

        my_dict.clear()  # remove all items from order so that a new order can be started
        return []




# track order
class TrackOrder(Action):
      def name(self):
            return "action_track_order"

      def run(self, dispatcher, tracker, domain):
            entities = tracker.latest_message['entities']
            cursor = conn.cursor()
            if len(entities)==0:
                  dispatcher.utter_message("आर्डर ट्रैक करने के लिए ट्रैक [आर्डर ID] लिखे")
            else:
                  id=int(entities[0]["value"])
                  query6="SELECT status FROM order_tracking where order_id=%s"
                  cursor.execute(query6,(id,))
                  status=cursor.fetchone()
                  if status:
                        dispatcher.utter_message(str(status[0]))
                  else:
                        dispatcher.utter_message("कोई टैक स्टेटस नहीं मिला .")
                  

            cursor.close()
            return []
      

