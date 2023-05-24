"""
List of all the events used
"""

events = {
    "CREATE_TASK": "CREATE_TASK", #sm.js- after success ajax req
    "JOIN": "JOIN", # sm,dp.js - After a user joins the socket
    "NEW_TASK": "NEW_TASK", # consumers- after creating new state, send ack to frontend
    "GET_NEW_TASK": "GET_NEW_TASK", # dp.js - after task acccepted get new task
    "TASK_ACCEPTED": "TASK_ACCEPTED", # dp.js - after user accept the task
    "TASK_DECLINED": "TASK_DECLINED", # dp.js - after user decline the task
    "TASK_CANCELLED": "TASK_CANCELLED", # sm.js - after user cancel the task
    "TASK_COMPLETED": "TASK_COMPLETED", # dp.js - after user complete the task
    "TASK_PENDING": "TASK_PENDING", # consumers - send ack to frontend about total pending task excced

    "TASK_CANCELLED_ACK": "TASK_CANCELLED_ACK", # consumers - after task is cancelled, send ack to frontend
    "TASK_COMPLETED_ACK": "TASK_COMPLETED_ACK", # consumers - after task is completed - send ack to dp user
    "TASK_DECLINED_ACK": "TASK_DECLINED_ACK",  # consumers - after task is declined - send ack to dp user
    "TASK_DECLINED_ACK_SM": "TASK_DECLINED_ACK_SM",  # consumers - after task is declined - send ack to sm user

    "LIST_STATES": "LIST_STATES", # sm.js get list of all states of task
    "LIST_STATES_REPLY": "LIST_STATES_REPLY", # reply of the list_state event
    "UPDATE_STATE": "UPDATE_STATE" #consumers - after creating new state, send ack to sm
}
