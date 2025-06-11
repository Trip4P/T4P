import React, { useEffect, useRef } from "react";

const KakaoMapView = ({ places }) => {
  const mapRef = useRef(null);
  const kakaoApiKey = import.meta.env.VITE_KAKAO_MAP_API_KEY;

  useEffect(() => {
    if (!mapRef.current) return;

    const script = document.createElement("script");
    script.src = `//dapi.kakao.com/v2/maps/sdk.js?appkey=${kakaoApiKey}&autoload=false&libraries=clusterer`;
    script.async = true;

    script.onload = () => {
      if (!window.kakao || !mapRef.current) return;

      window.kakao.maps.load(() => {
        const map = new window.kakao.maps.Map(mapRef.current, {
          center: new window.kakao.maps.LatLng(37.5665, 126.9780),
          level: 3,
        });

        const linePath = [];
        const markers = [];
        let polyline = null;

        places.forEach((place) => {
          const latlng = new window.kakao.maps.LatLng(place.lat, place.lng);
          linePath.push(latlng);

          const marker = new window.kakao.maps.Marker({
            map: map,
            position: latlng,
            title: place.name,
          });

          markers.push(marker);

          const infowindow = new window.kakao.maps.InfoWindow({
            content: `
              <div style="
                padding: 0;
                font-size: 13px;
                margin: 0;
                color: #000;
                white-space: nowrap;
                display: inline-block;
                background: transparent;
              ">
                <span style="
                  display: inline-block;
                  padding: 0;
                  margin: 0;
                  line-height: 1;
                ">
                  ${place.name}
                </span>
              </div>
            `,
          });

          window.kakao.maps.event.addListener(marker, "mouseover", () => {
            infowindow.open(map, marker);
          });

          window.kakao.maps.event.addListener(marker, "mouseout", () => {
            infowindow.close();
          });
        });

        if (places.length > 1) {
          new window.kakao.maps.MarkerClusterer({
            map: map,
            markers: markers,
            averageCenter: true,
            minLevel: 10,
          });
        }

        if (linePath.length > 1) {
          polyline = new window.kakao.maps.Polyline({
            path: linePath,
            strokeWeight: 5,
            strokeColor: "#0f62fe",
            strokeOpacity: 0.8,
            strokeStyle: "solid",
          });

          polyline.setMap(map);

          window.kakao.maps.event.addListener(map, "zoom_changed", () => {
            const currentLevel = map.getLevel();
            polyline.setMap(currentLevel > 10 ? null : map);
          });
        }

        if (linePath.length > 0) {
          map.setCenter(linePath[0]);

          if (linePath.length === 1) {
            map.setLevel(3);
          }
        }
      });
    };

    document.head.appendChild(script);
  }, [places, kakaoApiKey]);

  console.log(places);

  return (
    <div
      ref={mapRef}
      style={{ width: "100%", height: "400px", border: "1px solid #ddd" }}
    ></div>
  );
};

export default KakaoMapView;
