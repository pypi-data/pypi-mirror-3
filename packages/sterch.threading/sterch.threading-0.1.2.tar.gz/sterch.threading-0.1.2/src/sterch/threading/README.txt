 ---------------
 ZCML directives
 ---------------
1. Thread
 	<thread target="my_function"/>   
 	<thread target="my_function" name="My Thread"/>
 	
 	This will register two IThread utilities: with no name (default) and named "My Thread"
 	
2. Locks
 	<lock />   
 	<lock name="My Lock"/>
 	<rlock />   
 	<rlock name="My RLock"/>
 	
 	This will register two ILock and two IRLock utilities.
 	
3. Event	
 	<event />   
 	<event name="My Event"/>
 	
 	This will register two IEvent utilities: with no name (default) and named "My Event"

4. Condition	
    <condition />
    <condition name="My Condition"/>
    <condition lock="sterch.threading.tests.test_condition_directive.lock" 
               name="My Condition #2"/>
 	
 	This will register three ICondition utilities.

4. Semaphore	
    <semaphore />
    <semaphore name="My Semaphore" value="2"/>
 	
 	This will register two ISemaphore utilities.

5. Timer	
    <timer interval="10" function="sterch.threading.tests.test_timer_directive.fn"/>
    <timer interval="10" function="sterch.threading.tests.test_timer_directive.fn" name="My Timer"/>
 	
 	This will register two ITimer utilities.