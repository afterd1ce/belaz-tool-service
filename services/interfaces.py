from abc import ABC, abstractmethod


class IAuthService(ABC):
    @abstractmethod
    def login(self, badge_number: str, password: str) -> dict:
        pass

    @abstractmethod
    def refresh_token(self, refresh_token: str) -> dict:
        pass

    @abstractmethod
    def get_profile(self, user_id: str) -> dict:
        pass


class IInstrumentService(ABC):
    @abstractmethod
    def get_all(self, workshop: str | None, status: str | None, type: str | None) -> list[dict]:
        pass

    @abstractmethod
    def create(self, data) -> dict:
        pass

    @abstractmethod
    def get_by_id(self, inst_id: str) -> dict:
        pass

    @abstractmethod
    def update(self, inst_id: str, data) -> dict:
        pass

    @abstractmethod
    def delete(self, inst_id: str) -> dict:
        pass


class IMovementService(ABC):
    @abstractmethod
    def issue(self, barcode: str, worker_badge: str) -> dict:
        pass

    @abstractmethod
    def return_instrument(self, barcode: str, condition_ok: bool, notes: str | None) -> dict:
        pass

    @abstractmethod
    def get_history(self, inst_id: str) -> list[dict]:
        pass


class ICalibrationService(ABC):
    @abstractmethod
    def get_expired(self) -> list[dict]:
        pass

    @abstractmethod
    def verify(self, data) -> dict:
        pass

    @abstractmethod
    def daily_check(self) -> dict:
        pass