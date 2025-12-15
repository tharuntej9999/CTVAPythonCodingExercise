"""Tests for REST API endpoints."""

import json


class TestWeatherEndpoint:
    """Test cases for /api/weather endpoint."""

    def test_get_weather_records(self, client, sample_weather_data):
        """Test getting all weather records."""
        response = client.get("/api/weather")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert "data" in data
        assert "pagination" in data
        assert len(data["data"]) == 5

    def test_filter_by_station_id(self, client, sample_weather_data):
        """Test filtering by station ID."""
        response = client.get("/api/weather?station_id=USC00110072")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert len(data["data"]) == 3
        for record in data["data"]:
            assert record["station_id"] == "USC00110072"

    def test_filter_by_date(self, client, sample_weather_data):
        """Test filtering by specific date."""
        response = client.get("/api/weather?date=1985-01-01")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert len(data["data"]) == 2
        for record in data["data"]:
            assert record["date"] == "1985-01-01"

    def test_filter_by_date_range(self, client, sample_weather_data):
        """Test filtering by date range."""
        response = client.get("/api/weather?start_date=1985-01-01&end_date=1985-01-02")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert len(data["data"]) == 3

    def test_pagination(self, client, sample_weather_data):
        """Test pagination."""
        response = client.get("/api/weather?page=1&page_size=2")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert len(data["data"]) == 2
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["page_size"] == 2
        assert data["pagination"]["total_records"] == 5

    def test_invalid_date_format(self, client, sample_weather_data):
        """Test that invalid date format returns error."""
        response = client.get("/api/weather?date=2024-13-45")
        assert response.status_code == 400

        data = json.loads(response.data)
        assert "error" in data

    def test_temperature_conversion(self, client, sample_weather_data):
        """Test that temperatures are converted from tenths to degrees."""
        response = client.get("/api/weather?station_id=USC00110072&date=1985-01-01")
        assert response.status_code == 200

        data = json.loads(response.data)
        record = data["data"][0]

        assert record["max_temp"] == -2.2

        assert record["min_temp"] == -12.8

        assert record["precipitation"] == 9.4


class TestWeatherStatsEndpoint:
    """Test cases for /api/weather/stats endpoint."""

    def test_get_weather_stats(self, client, sample_weather_stats):
        """Test getting all weather stats."""
        response = client.get("/api/weather/stats")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert "data" in data
        assert "pagination" in data
        assert len(data["data"]) == 3

    def test_filter_by_station_id(self, client, sample_weather_stats):
        """Test filtering stats by station ID."""
        response = client.get("/api/weather/stats?station_id=USC00110072")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert len(data["data"]) == 1
        assert data["data"][0]["station_id"] == "USC00110072"

    def test_filter_by_year(self, client, sample_weather_stats):
        """Test filtering stats by year."""
        response = client.get("/api/weather/stats?year=1985")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert len(data["data"]) == 2
        for stat in data["data"]:
            assert stat["year"] == 1985

    def test_filter_by_year_range(self, client, sample_weather_stats):
        """Test filtering stats by year range."""
        response = client.get("/api/weather/stats?start_year=1985&end_year=1986")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert len(data["data"]) == 3

    def test_pagination(self, client, sample_weather_stats):
        """Test pagination for stats."""
        response = client.get("/api/weather/stats?page=1&page_size=2")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert len(data["data"]) == 2
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["page_size"] == 2
        assert data["pagination"]["total_records"] == 3

    def test_stats_values(self, client, sample_weather_stats):
        """Test that stats values are correctly formatted."""
        response = client.get("/api/weather/stats?station_id=USC00110187&year=1985")
        assert response.status_code == 200

        data = json.loads(response.data)
        stats = data["data"][0]

        assert stats["avg_max_temp"] == 5.0
        assert stats["avg_min_temp"] == -5.0
        assert stats["total_precipitation"] == 1.0


class TestSwaggerDocumentation:
    """Test cases for Swagger documentation."""

    def test_swagger_endpoint_exists(self, client):
        """Test that Swagger documentation is available."""
        response = client.get("/api/docs")
        assert response.status_code == 200

    def test_swagger_json_exists(self, client):
        """Test that Swagger JSON spec is available."""
        response = client.get("/api/swagger.json")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert "info" in data
        assert "paths" in data
        assert "/weather" in data["paths"]
        assert "/weather/stats" in data["paths"]
