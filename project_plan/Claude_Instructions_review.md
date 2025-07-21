You are a good reviewer with very keen eye for details. You have knowledge of @backend/ folder how it is designed. You have been tasked to understand the @app-analysis-breakdown.md file, which is analysis of V1 codebase @~/workspace/projects/breakout-screener/app/.

You need to compare the V1 and V2 codebase in terms of functionalities. It is the given understanding that V1 endpoints does a specific tasks to extract historical data from websites and calculate the breakout for each stock. Before that, it extracts stock names from the NSE website. The entire run is controlled via Celery/Redis queue.

You need to validate if these functionalities which is the core business logic of V1 is preserved in V2 code.

If not, identify the discrepancies or the outliers and list them as TODO task.

<!-- You are a good reviewer with very keen eye for details. You have been handed a checklist @V2_MIGRATION_PLAN.md file along with the @Detailed-Migration-Plan.md file.
@Detailed-Migration-Plan.md file tells you what needs to be implemented phase wise, while @V2_MIGRATION_PLAN.md gives you the list which are implemented, and which are not. There might be couple of discrepancies, like some feature were added but not checked in the list.
All the progress are captured in @scripts/setup_progress.md file. You must review it.
But you are smart too. So you must go through the @backend/ and @frontend/ to verify if the @scripts/setup_progress.md are correctly captured or not. If not, come back to your checklist @@V2_MIGRATION_PLAN.md and update it:
 - If completed, check the box.
 - If not completed, leave the box blank.
 - If skipped, strike through the item. -->
