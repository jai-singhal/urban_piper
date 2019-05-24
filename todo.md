# context["pending_tasks"] = user_tasks.filter(
#     state__state = "accepted", 
# ).values("task__id", "task__title", "task__creation_at").difference(
#     user_tasks.filter(
#         state__state = "completed", 
#     ).values("task__id", "task__title", "task__creation_at")
# ).difference(
#     user_tasks.filter(
#         state__state = "declined", 
#     ).values("task__id", "task__title", "task__creation_at")
# )



curl --include \
     --no-buffer \
     --header "Connection: Upgrade" \
     --header "Upgrade: websocket" \
     --header "Host: 159.65.148.37:8000" \
     --header "Origin: http://159.65.148.37:8000" \
     --header "Sec-WebSocket-Key: SGVsbG8sIHdvcmxkIQ==" \
     --header "Sec-WebSocket-Version: 13" \
     http://159.65.148.37:8000/