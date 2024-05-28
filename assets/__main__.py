from typing import Tuple

# python -m pip install maafw
from maa.define import RectType
from maa.resource import Resource
from maa.controller import AdbController
from maa.instance import Instance
from maa.instance import TaskDetail
from maa.toolkit import Toolkit

from maa.custom_recognizer import CustomRecognizer
from maa.custom_action import CustomAction

import asyncio
import re

tili_buy_ct = 2


async def main():
    user_path = "./"
    Toolkit.init_option(user_path)

    resource = Resource()
    await resource.load("/Users/didi/CodeSelf/MaaMaiFen/assets/resource/base")

    device_list = await Toolkit.adb_devices()
    if not device_list:
        print("No ADB device found.")
        exit()

    # for demo, we just use the first device
    device = device_list[0]
    controller = AdbController(
        adb_path=device.adb_path,
        address=device.address,
    )
    await controller.connect()

    maa_inst = Instance()
    maa_inst.bind(resource, controller)

    if not maa_inst.inited:
        print("Failed to init MAA.")
        exit()

    while True:
        # 日常任务
        await daily_task(maa_inst)
        # 试炼任务
        await shilian_task(maa_inst)


async def daily_task(maa_inst: Instance) -> bool:
    # 返回首页
    await maa_inst.run_task("首页-冒险-标识")

    # 执行一键强化
    await maa_inst.run_task("首页-行李-跳转")
    await maa_inst.run_task("一键强化")
    # 执行技能升级
    await maa_inst.run_task("首页-旅人-跳转")
    await maa_inst.run_task("技能升级")

    # 营地任务
    await maa_inst.run_task("首页-营地-标识")
    # 执行邮件领取
    await maa_inst.run_task("营地-邮箱")
    # 执行旅行活动
    await maa_inst.run_task("营地-旅行活动")
    await maa_inst.run_task("营地-旅行活动-爱心发射")

    return True


# 试炼-秘境之间
async def mijing_task(maa_inst: Instance) -> bool:
    await maa_inst.run_task("首页-冒险-标识")

    res = await maa_inst.run_task("首页-试炼-跳转")
    if is_task_hit_v2(res, "首页-试炼-跳转"):
        await maa_inst.run_task("试炼-秘境之间-跳转")
        await maa_inst.run_task("秘境之间-永冻禁区矿场")

    # 补充体力判断
    await tili_goumai(maa_inst, tili_buy_ct)
    # 试炼任务
    fight_ct = 0
    start_time = asyncio.get_event_loop().time()
    while True:
        res = await maa_inst.run_task("试炼-开始挑战")
        # 判断当前状态
        if is_task_hit_v2(res, "开始匹配"):
            await maa_inst.run_task("体力不足-提示")
            if is_task_hit_v2(res, "体力不足-提示"):
                is_task_hit_v2(res, "确定", "体力不足确认")
        is_task_hit_v2(res, "准备", "匹配成功")
        # is_task_hit_v2(res, "取消", "匹配超时")  # 匹配超时，点击取消
        is_task_hit_v2(res, "离开队伍")
        if is_task_hit_v2(res, "战斗中"):
            await wait_fight_done(maa_inst)
            start_time = asyncio.get_event_loop().time()  # 重置匹配超时时间
            fight_ct += 1
            print(f"挑战完成，已进行{fight_ct}次，等待执行下一轮")
        if asyncio.get_event_loop().time() - start_time >= 600:
            print("秘境匹配10min超时，退出")
            break

        if fight_ct > 5:
            print(f"挑战结束，已进行{fight_ct}次，执行下一个任务")
            break
        print("秘境任务中")
        # 休息3s
        await asyncio.sleep(3)


# 试炼-绝境挑战
async def juejing_task(maa_inst: Instance) -> bool:
    await maa_inst.run_task("首页-冒险-标识")

    res = await maa_inst.run_task("首页-试炼-跳转")
    if is_task_hit_v2(res, "首页-试炼-跳转"):
        await maa_inst.run_task("试炼-绝境挑战-跳转")

    # 试炼任务
    fight_ct = 0
    start_time = asyncio.get_event_loop().time()
    while True:
        res = await maa_inst.run_task("试炼-开始挑战")
        # 判断当前状态
        is_task_hit_v2(res, "开始匹配")
        is_task_hit_v2(res, "准备", "匹配成功")
        # is_task_hit_v2(res, "取消", "匹配超时")  # 匹配超时，点击取消
        is_task_hit_v2(res, "离开队伍")
        if is_task_hit_v2(res, "战斗中"):
            await wait_fight_done(maa_inst)
            start_time = asyncio.get_event_loop().time()  # 重置匹配超时时间
            fight_ct += 1
            print(f"挑战完成，已进行{fight_ct}次，等待执行下一轮")
        if asyncio.get_event_loop().time() - start_time >= 600:
            print("绝境匹配10min超时，退出")
            break

        if fight_ct > 1:
            print(f"挑战结束，已进行{fight_ct}次，执行下一个任务")
            break
        print(f"绝境任务中，等待挑战开始，已运行{asyncio.get_event_loop().time() - start_time}秒")
        # 休息3s
        await asyncio.sleep(3)


async def shilian_task(maa_inst: Instance):
    await mijing_task(maa_inst)
    await juejing_task(maa_inst)


# 体力购买
async def tili_goumai(maa_inst: Instance, want_buy_ct: int = 3) -> bool:
    await maa_inst.run_task("体力按钮-点击")
    res = await maa_inst.run_task("每日限购-剩余次数")
    text = res.node_details[0].recognition.detail["best"]["text"]
    buy_ct = int(text.replace("每日限购（", "").replace("/3）", ""))
    # 判断体力购买
    if buy_ct < want_buy_ct:
        await maa_inst.run_task("购买按钮-点击")
        is_task_hit_v2(res, "购买按钮-点击", "体力购买1次")
    await maa_inst.run_task("返回-单次")
    return True


async def wait_fight_done(maa_inst: Instance) -> bool:
    start_time = asyncio.get_event_loop().time()
    other_task_flag = False
    while True:
        res = await maa_inst.run_task("战斗-等待结束")
        if is_task_hit_v2(res, "战败确认"):
            await maa_inst.run_task("放弃")
            break
        if is_task_hit_v2(res, "领取宝箱-开启宝箱"):
            break
        if is_task_hit_v2(res, "领取宝箱-体力不足"):
            break
        if asyncio.get_event_loop().time() - start_time >= 600:
            print("秘境挑战10min超时，退出")
            break

        # 执行一次：行李-一键强化、旅人-技能升级
        if not other_task_flag:
            other_task_flag = True
            await maa_inst.run_task("首页-行李-跳转")
            await maa_inst.run_task("一键强化")
            await maa_inst.run_task("首页-旅人-跳转")
            await maa_inst.run_task("技能升级")
            await maa_inst.run_task("首页-冒险-跳转")

        print("挑战中")
        await asyncio.sleep(3)


def is_task_hit(task: TaskDetail, node_num: int = 0):
    if task is None:
        return False
    node_details = task.node_details
    if node_details is None or len(node_details) == 0:
        return False
    first_element = node_details[node_num]
    return first_element.recognition.hit_box.x > 0


def is_task_hit_v2(task: TaskDetail, node_name: str, hit_remark: str = ""):
    if task is None:
        return False
    node_details = task.node_details
    if node_details is None or len(node_details) == 0:
        return False

    flag = False
    for i, res in enumerate(node_details):
        if res.name == node_name:
            flag = res.recognition.detail["best"]["score"] > 0
    if flag:
        if hit_remark == "":
            hit_remark = node_name
        print(hit_remark)

    return flag


if __name__ == "__main__":
    asyncio.run(main())
