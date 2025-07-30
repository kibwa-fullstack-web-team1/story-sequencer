from datetime import datetime

class DynamicMock:
    def __init__(self, service_name="MockService"):
        self.service_name = service_name
        self._method_responses = {}

    def init_app(self, app):
        return self

    def __getattr__(self, name):
        def mock_method(*args, **kwargs):
            print(f"[{self.service_name}] Called: {name}({args}, {kwargs})")

            if name in self._method_responses:
                return self._method_responses[name]

            return self._generate_default_response(name, args, kwargs)

        return mock_method

    def _generate_default_response(self, method_name, args, kwargs):
        if method_name.startswith('get_'):
            if 'list' in method_name or method_name.endswith('s'):
                return []
            return {}
        elif method_name.startswith('create_') or method_name.startswith('add_'):
            return {"id": f"mock_{datetime.now().timestamp()}", "status": "created"}
        elif 'ping' in method_name:
            return {args[0]: True} if args else True
        elif 'run' in method_name or 'execute' in method_name:
            target = args[0] if args else "unknown"
            return {
                target: {
                    "retcode": 0,
                    "stdout": f"Mock execution successful",
                    "stderr": "",
                    "success": True
                }
            }
        return {"mock": True, "method": method_name, "response": "default"} 