import { useEffect } from "react";

export default function GoogleMapView({ places }) {
  useEffect(() => {
    if (window.google) {
      initMap();
      return;
    }

    const script = document.createElement("script");
    script.src = `https://maps.googleapis.com/maps/api/js?key=${
      import.meta.env.VITE_GOOGLE_MAP_API_KEY
    }&libraries=places`;
    script.async = true;
    script.defer = true;
    script.onload = () => {
      initMap();
    };
    document.head.appendChild(script);
  }, [places]);

  const initMap = () => {
    const map = new window.google.maps.Map(document.getElementById("map"), {
      center: { lat: places[0].lat, lng: places[0].lng },
      zoom: 13,
    });

    const pathCoords = [];

    places.forEach((place) => {
      const marker = new window.google.maps.Marker({
        position: { lat: place.lat, lng: place.lng },
        map,
        title: place.name,
      });

      const infoWindow = new window.google.maps.InfoWindow({
        content: `<div style="font-size:14px;"><strong>${
          place.name
        }</strong><br/>${place.description || ""}</div>`,
      });

      marker.addListener("click", () => {
        infoWindow.open(map, marker);
      });

      pathCoords.push({ lat: place.lat, lng: place.lng });
    });

    const polyline = new window.google.maps.Polyline({
      path: pathCoords,
      geodesic: true,
      strokeColor: "#4285F4",
      strokeOpacity: 0.8,
      strokeWeight: 4,
      icons: [
        {
          icon: {
            path: window.google.maps.SymbolPath.FORWARD_CLOSED_ARROW,
            scale: 3, // 화살표 크기
            strokeColor: "#4285F4",
          },
          offset: "100%", // 어디에 표시할지 (100%는 끝 부분)
        }
      ]
    });
    polyline.setMap(map);
  };

  return <div id="map" style={{ height: "400px", width: "100%" }} />;
}
