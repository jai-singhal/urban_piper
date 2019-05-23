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
