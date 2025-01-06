from datetime import datetime
from celery import Task

from datetime import datetime, timezone
import logging


class BaseTask(Task):
    """
    Custom base class for Celery tasks that tracks the start and end times,
    logs task execution information, and updates the task's state with
    metadata including the result or error details.

    Attributes:
        start_time (str): The start time of the task execution in ISO format.
    """

    def __init__(self):
        """Initialize the task and set the start time."""
        super().__init__()
        self.start_time = datetime.now(timezone.utc).isoformat()

    def __call__(self, *args, **kwargs):
        """
        Execute the task, updating the state and logging execution details.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            The result of the task execution.

        Raises:
            Exception: Re-raises any exception encountered during task execution.
        """
        self.start_time = datetime.now(timezone.utc).isoformat()
        logging.info("Task %s started at %s", self.name, self.start_time)
        self.update_state(state="STARTED", meta={
                          "start_time": self.start_time})

        try:
            # Call the original task logic and capture the result
            result = super().__call__(*args, **kwargs)
            end_time = datetime.now(timezone.utc).isoformat()

            # Update state with SUCCESS and timing metadata
            self.update_state(
                state="SUCCESS",
                meta={**result,
                      "start_time": self.start_time,
                      "end_time": end_time,
                      }
            )
            logging.info("Task %s ended at %s", self.name, end_time)
            return result

        except Exception as e:
            end_time = datetime.utcnow().isoformat()
            self.update_state(
                state="FAILURE",
                meta={
                    "start_time": self.start_time,
                    "end_time": end_time,
                    "error": e,
                },
            )
            logging.info("Task %s failed at %s: %s",
                         self.name, end_time, str(e))
            raise e


class BaseTaskWithTiming(Task):
    def __call__(self, *args, **kwargs):
        """
        Override the __call__ method to cleanly separate task result from metadata.
        """
        self.start_time = datetime.utcnow().isoformat()
        self.update_state(state="STARTED", meta={
                          "start_time": self.start_time})

        try:
            # Call the original task logic and capture the result
            result = super().__call__(*args, **kwargs)
            end_time = datetime.utcnow().isoformat()
            logging.info(result)
            # Update only timing in the meta, result is returned separately
            # self.update_state(
            #     state="SUCCESS",
            #     meta={"start_time": self.start_time, "end_time": end_time}
            # )
            result["start_time"] = self.start_time
            result["end_time"] = end_time

            return result  # Return the task's actual result directly

        except Exception as e:
            end_time = datetime.utcnow().isoformat()

            # Update only timing and error metadata
            self.update_state(
                state="FAILURE",
                meta={
                    "start_time": self.start_time,
                    "end_time": end_time,
                    "error": str(e),
                }
            )
            raise e
