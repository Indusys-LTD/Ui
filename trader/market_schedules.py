from datetime import datetime, time, timedelta
import pytz

class MarketSchedules:
    def __init__(self):
        # Define market sessions with their respective timezones
        self.sessions = {
            'Sydney': {
                'timezone': pytz.timezone('Australia/Sydney'),
                'open': time(7, 0),  # 7:00 AM Sydney time
                'close': time(16, 0)  # 4:00 PM Sydney time
            },
            'Tokyo': {
                'timezone': pytz.timezone('Asia/Tokyo'),
                'open': time(9, 0),   # 9:00 AM Tokyo time
                'close': time(18, 0)  # 6:00 PM Tokyo time
            },
            'London': {
                'timezone': pytz.timezone('Europe/London'),
                'open': time(8, 0),   # 8:00 AM London time
                'close': time(17, 0)  # 5:00 PM London time
            },
            'New York': {
                'timezone': pytz.timezone('America/New_York'),
                'open': time(8, 0),   # 8:00 AM New York time
                'close': time(17, 0)  # 5:00 PM New York time
            }
        }

    def is_weekend(self, dt=None):
        """Check if the current time is weekend."""
        if dt is None:
            dt = datetime.now(pytz.UTC)
        return dt.weekday() >= 5  # 5 is Saturday, 6 is Sunday

    def get_active_sessions(self, dt=None):
        """Get currently active market sessions."""
        if dt is None:
            dt = datetime.now(pytz.UTC)
        
        if self.is_weekend(dt):
            return []

        active_sessions = []
        
        for session_name, session_info in self.sessions.items():
            # Convert current UTC time to session's timezone
            session_time = dt.astimezone(session_info['timezone'])
            current_time = session_time.time()
            
            # Check if market is open
            if session_info['open'] <= current_time < session_info['close']:
                active_sessions.append(session_name)
        
        return active_sessions

    def get_market_state(self):
        """Get comprehensive market state information."""
        current_time = datetime.now(pytz.UTC)
        
        state = {
            'timestamp': current_time,
            'is_weekend': self.is_weekend(current_time),
            'active_sessions': self.get_active_sessions(current_time),
            'session_times': {}
        }

        # Add local times for each session
        for session_name, session_info in self.sessions.items():
            local_time = current_time.astimezone(session_info['timezone'])
            state['session_times'][session_name] = {
                'local_time': local_time,
                'is_open': session_info['open'] <= local_time.time() < session_info['close']
            }

        return state

    def is_market_open(self):
        """Check if any market is currently open."""
        if self.is_weekend():
            return False
        return len(self.get_active_sessions()) > 0

    def get_next_market_open(self, dt=None):
        """Get the next market session to open."""
        if dt is None:
            dt = datetime.now(pytz.UTC)
            
        if not self.is_weekend(dt) and self.is_market_open():
            return None  # Market is already open
            
        next_open = None
        next_session = None
        
        for session_name, session_info in self.sessions.items():
            session_time = dt.astimezone(session_info['timezone'])
            session_open = datetime.combine(session_time.date(), session_info['open'])
            
            # If current time is past today's open, look at tomorrow's open
            if session_time.time() >= session_info['open']:
                session_open = session_open + timedelta(days=1)
                
            session_open = session_info['timezone'].localize(session_open)
            
            if next_open is None or session_open < next_open:
                next_open = session_open
                next_session = session_name
                
        return {
            'session': next_session,
            'open_time': next_open
        }

