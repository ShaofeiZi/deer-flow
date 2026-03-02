#!/usr/bin/env python
"""
lead_agent 调试脚本。
可在 VS Code 中直接运行此文件进行断点调试。

使用方法：
    1. 在 agent.py 或其他文件中设置断点
    2. 按 F5 或使用"运行和调试"面板
    3. 在终端中输入消息与代理交互
"""

import asyncio
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

from src.agents import make_lead_agent

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


async def main():
    try:
        from src.mcp import initialize_mcp_tools

        await initialize_mcp_tools()
    except Exception as e:
        print(f"警告：MCP 工具初始化失败：{e}")

    config = {
        "configurable": {
            "thread_id": "debug-thread-001",
            "thinking_enabled": True,
            "is_plan_mode": True,
            "model_name": "kimi-k2.5",
        }
    }

    agent = make_lead_agent(config)

    print("=" * 50)
    print("Lead Agent 调试模式")
    print("输入 'quit' 或 'exit' 退出")
    print("=" * 50)

    while True:
        try:
            user_input = input("\n你: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("quit", "exit"):
                print("再见！")
                break

            state = {"messages": [HumanMessage(content=user_input)]}
            result = await agent.ainvoke(state, config=config, context={"thread_id": "debug-thread-001"})

            if result.get("messages"):
                last_message = result["messages"][-1]
                print(f"\n代理: {last_message.content}")

        except KeyboardInterrupt:
            print("\n已中断。再见！")
            break
        except Exception as e:
            print(f"\n错误: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
