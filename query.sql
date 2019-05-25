select task.title, task.creation_at, task.priority, task.created_by_id
from core_deliverytask as task, 
	(
		select temp2.task_id
		from (
		    select task_id, MAX(at) as max_at1
		    from core_deliverystatetransition
		    group by task_id
		) as temp1,
		core_deliverystatetransition as temp2, core_deliverytaskstate as states
		where states.id = temp2.state_id and states.state = 'accepted'
		and temp1.task_id = temp2.task_id and temp1.max_at1 = temp2.at

	) as trans
where trans.task_id=task.id;
