"""
统一日志模块 — 按任务 ID 记录 Fusion 自动化操作

日志层级:
  INFO   关键步骤、成功结果
  DEBUG  工具调用详情、参数摘要
  WARN   非致命异常
  ERROR  失败和恢复尝试

日志格式:
  [2026-10-26 14:30:00] [task_id=abc123] [level] message
"""

import logging
import os
import sys
from datetime import datetime
from typing import Optional


def setup_logger(name: str = "yunwei", log_dir: str = "logs", level: str = "INFO") -> logging.Logger:
    """
    创建并配置 logger

    Args:
        name: logger 名称
        log_dir: 日志目录（如不存在会创建）
        level: DEBUG / INFO / WARN / ERROR
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  # 已初始化

    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # 统一格式
    fmt = logging.Formatter(
        "[%(asctime)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 控制台输出
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    # 文件输出（如目录可写）
    try:
        os.makedirs(log_dir, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        fh = logging.FileHandler(os.path.join(log_dir, f"yunwei_{ts}.log"), encoding="utf-8")
        fh.setFormatter(fmt)
        logger.addHandler(fh)
    except PermissionError:
        print(f"⚠️  无法写入 {log_dir}/ 日志目录 — 日志只输出到终端", file=sys.stderr)

    logger.propagate = False
    return logger


def log_task(logger: logging.Logger, task_id: str, level: str, message: str):
    """带 task_id 的结构化日志"""
    prefix = f"[task_id={task_id}]"
    getattr(logger, level.lower())(f"{prefix} {message}")


class TaskLogger:
    """任务级日志上下文管理器"""

    def __init__(self, task_id: str, logger: Optional[logging.Logger] = None):
        self.task_id = task_id
        self.logger = logger or logging.getLogger("yunwei")

    def info(self, msg: str):
        log_task(self.logger, self.task_id, "INFO", msg)

    def debug(self, msg: str):
        log_task(self.logger, self.task_id, "DEBUG", msg)

    def warn(self, msg: str):
        log_task(self.logger, self.task_id, "WARNING", msg)

    def error(self, msg: str):
        log_task(self.logger, self.task_id, "ERROR", msg)

    def step(self, n: int, total: int, desc: str):
        self.info(f"[{n}/{total}] {desc}")


if __name__ == "__main__":
    logger = setup_logger(level="DEBUG")
    tl = TaskLogger("test-001", logger)
    tl.step(1, 3, "连接 Fusion MCP")
    tl.info("Session established")
    tl.step(2, 3, "创建立方体")
    tl.info("Cube created, volume=8000 cm³")
    tl.step(3, 3, "导出 STEP/STL")
    tl.debug("STEP path: models/test_cube.step")
    tl.info("✅ 全链路通过")
