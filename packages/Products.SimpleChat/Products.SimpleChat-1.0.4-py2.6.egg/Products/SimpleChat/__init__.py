import SimpleChat

def initialize(context): 
    """Initialize."""
    try:
        """Try to register the product."""
        context.registerClass(
            SimpleChat.SimpleChat,
            constructors = (
                SimpleChat.manage_add_simple_chat_form,
                SimpleChat.manage_add_simple_chat),
            )

    except:
        import sys, traceback, string
        type, val, tb = sys.exc_info()
        sys.stderr.write(string.join(
            traceback.format_exception(type, val, tb), ''))
        del type, val, tb
