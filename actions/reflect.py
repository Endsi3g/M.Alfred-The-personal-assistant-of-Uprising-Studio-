from scripts.self_improvement import MissionReflector

def reflect(jarvis_obj=None):
    """
    Tactical Action: Alfred reflects on execution data to refine mission protocols.
    """
    try:
        reflector = MissionReflector()
        report = reflector.analyze_recent_failures()
        
        # Log to the UI/Console
        if jarvis_obj:
            jarvis_obj.speak(f"Master Bell, I have completed a tactical reflection. {report.split('.')[0]}.")
            
        return {
            "status": "protocol_optimized",
            "reflection": report
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    print(reflect())
