import requests

from app.passfort.types import EventsCallback


class Client:
    def __init__(self, callback_url):
        self.callback_url = callback_url

    def send_events(self, portfolio_id, portfolio_name, end_date, events, raw):
        response = requests.post(
            self.callback_url,
            json=EventsCallback(
                {
                    "portfolio_id": portfolio_id,
                    "portfolio_name": portfolio_name,
                    "end_date": end_date,
                    "events": events,
                    "raw": raw,
                }
            ).to_primitive(),
        )
        response.raise_for_status()
