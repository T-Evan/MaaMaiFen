from typing import Tuple

# ... (其他导入保持不变)

async def main():
    # ... (其他代码保持不变)

    maa_inst.register_recognizer("MyRec", my_rec)
    maa_inst.register_action("DailyAct", daily_act_with_maa_instance(maa_inst))

    await maa_inst.run_task("日常任务")


class DailyAction:
    def __init__(self, maa_inst):
        self.maa_inst = maa_inst

    async def run(self, context, task_name, custom_param, box, rec_detail) -> bool:
        await self.行李任务A(context)
        # ... (其他代码保持不变)

    async def 行李任务A(self, context) -> bool:
        # 使用 `await` 等待异步任务完成
        await self.maa_inst.run_task("首页-行李-标识")
        # ... (其他代码保持不变)

    def stop(self) -> None:
        pass


def daily_act_with_maa_instance(maa_inst):
    action = DailyAction(maa_inst)
    return lambda *args, **kwargs: asyncio.coroutine(action.run)(*args, **kwargs)


my_rec = MyRecognizer()
daily_act = daily_act_with_maa_instance(maa_inst)

if __name__ == "__main__":
    asyncio.run(main())
