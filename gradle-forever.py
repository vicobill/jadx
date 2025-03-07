import subprocess
import time
import sys

def run_command_with_retry(cmd, max_retries=3, timeout=10, initial_wait=1):
    """
    执行外部命令，失败时自动重试。

    参数:
        cmd (str): 要执行的命令字符串
        max_retries (int): 最大重试次数，默认3次
        timeout (int): 命令执行超时时间（秒），默认10秒
        initial_wait (int): 初始重试等待时间（秒），默认1秒

    返回:
        str: 命令成功执行的输出

    异常:
        RuntimeError: 所有重试均失败后抛出
    """
    for attempt in range(max_retries):
        try:
            # 执行命令，捕获输出和错误，设置超时
            result = subprocess.run(
                cmd,
                shell=True,          # 注意：可能存在安全风险，仅用于简单命令
                check=True,           # 非零退出码会引发异常
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout
            )
            return result.stdout.decode('utf-8')
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            # 记录错误信息
            error_msg = f"Attempt {attempt + 1} failed: {e}\n"
            if isinstance(e, subprocess.CalledProcessError):
                error_msg += f"Exit Code: {e.returncode}\nStderr: {e.stderr.decode('utf-8')}"
            print(error_msg, file=sys.stderr)

            # 检查是否还有剩余重试机会
            # if attempt >= max_retries - 1:
            #     raise RuntimeError(f"All {max_retries} attempts failed for command: {cmd}") from e

            # 指数退避等待
            wait_time = initial_wait #* (2 ** attempt)
            print(f"Retrying in {wait_time:.2f} seconds...", file=sys.stderr)
            time.sleep(wait_time)

    # 此处理论上不会到达，因为前面已经抛出异常
    raise RuntimeError("Unexpected error during command execution.")

# 示例用法
if __name__ == "__main__":
    try:
        output = run_command_with_retry("gradlew.bat --info --rerun-tasks", max_retries=500, timeout=15)
        print("Command succeeded:")
        print(output)
    except Exception as e:
        print(f"Final failure: {e}", file=sys.stderr)
