from django.dispatch import Signal

goal_recorded = Signal(providing_args=['goal_record', 'experiment_user'])