from Backend.model.User import mongo
from datetime import datetime, timedelta

states = mongo.db.states

def getLastSessionData(document_id):
    try:
        # Find the document
        document = states.find_one({"_id": document_id})
        
        if not document or 'state' not in document:
            return {
                'stress': 0,
                'anxiety': 0,
                'anger': 0
            }

        # Get all dates and sort them
        dates = list(document['state'].keys())
        if not dates:
            return {
                'stress': 0,
                'anxiety': 0,
                'anger': 0
            }

        # Get the latest date
        latest_date = max(dates)
        
        # Get the latest session data
        latest_sessions = document['state'][latest_date]
        
        if not latest_sessions:
            return {
                'stress': 0,
                'anxiety': 0,
                'anger': 0
            }

        return latest_sessions[-1]

    except Exception as e:
        print(f"Error getting last session data: {str(e)}")
        return {
            'stress': 0,
            'anxiety': 0,
            'anger': 0
        }

def getTodaysSessionData(document_id):
    try:
        pipeline = [
            {
                '$match': { '_id': document_id }  
            },
            {
                '$project': {
                    'latestDate': {
                        '$arrayElemAt': [
                            { '$sortArray': { 'input': { '$objectToArray': '$state' }, 'sortBy': { 'k': -1 } } },
                            0
                        ]
                    }
                }
            },
            {
                '$project': {
                    'date': '$latestDate.k',  
                    'data': '$latestDate.v'   
                }
            }
        ]
        result = list(states.aggregate(pipeline))
        result = result[0]
        data = result['data']
        return data if result else {}
    except Exception as e:
        print(f"Error getting today's session data: {str(e)}")
        return {}


def getPastFiveDaysSessionData(document_id):
    try:
        today = datetime.now()
        past_dates = [(today - timedelta(days=i)).strftime("%d-%m-%Y") for i in range(5)]
        
        # Get the document directly instead of using aggregation
        document = states.find_one({"_id": document_id})
        
        response_data = {}
        if document and 'state' in document:
            state_data = document['state']
            
            # Sort dates in descending order
            sorted_dates = sorted(state_data.keys(), reverse=True)
            
            # Get the 5 most recent dates with data
            recent_dates = sorted_dates[:5] if sorted_dates else []
            
            # Fill in data for available dates
            for date in recent_dates:
                daily_data = state_data[date]
                if daily_data:
                    stress_avg = sum(entry['stress'] for entry in daily_data) / len(daily_data)
                    anxiety_avg = sum(entry['anxiety'] for entry in daily_data) / len(daily_data)
                    anger_avg = sum(entry['anger'] for entry in daily_data) / len(daily_data)
                    response_data[date] = {
                        'stress': round(stress_avg, 2),
                        'anxiety': round(anxiety_avg, 2),
                        'anger': round(anger_avg, 2)
                    }
            
            # Fill remaining dates with zeros if needed
            remaining = 5 - len(response_data)
            if remaining > 0:
                for i in range(remaining):
                    date = (today - timedelta(days=len(response_data))).strftime("%d-%m-%Y")
                    response_data[date] = {
                        'stress': 0,
                        'anxiety': 0,
                        'anger': 0
                    }
                    
        return response_data
        
    except Exception as e:
        print(f"Error getting past five days data: {str(e)}")
        return {}





def appendSessionData(document_id, stress, anxiety, anger):
    current_time = datetime.now().strftime("%d-%m-%Y")
    new_data = {
        "stress": stress,
        "anxiety": anxiety,
        "anger": anger,
    }
    document = states.find_one({"_id": document_id})

    if document:
        if current_time in document.get('state', {}):
            result = states.update_one(
                { "_id": document_id },
                { "$push": { f"state.{current_time}": new_data } }
            )
        else:
            result = states.update_one(
                { "_id": document_id },
                { "$set": { f"state.{current_time}": [new_data] } } 
            )
    else:
        result = states.insert_one({
            "_id": document_id,
            "state": { current_time: [new_data] }
        })

    return result.modified_count > 0 or result.upserted_id is not None



