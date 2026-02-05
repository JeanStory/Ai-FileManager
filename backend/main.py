from app.core.session import Session

if __name__ == "__main__":
    session = Session("test_session", "test_user_1")
    output=session.chat("查询人工智能相关的内容")
    print(output)
