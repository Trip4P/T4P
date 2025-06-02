// KakaoMap.jsx
import React, { useEffect, useRef } from "react";

const KakaoMapView  = ({ places }) => {
  const mapRef = useRef(null); //useRef로 div 참조
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
            // map,
            position: latlng,
            title: place.name,
          });

          markers.push(marker);

          const infowindow = new window.kakao.maps.InfoWindow({
            content: 
            `<div style = "
            padding:0; 
            font-size:13px;
            margin:0;
            color:ffff;
            white-space:nowrap;
            display:inline-block;
            disableAutoPan:true;
            background:transparent;
            ">
            <span style="
            display:inline-block;
            padding:0;
            margin:0;
            line-height:1;
            ">
            ${place.name}</span>
            <div>`,
          });

          window.kakao.maps.event.addListener(marker, "mouseover", () => {
            infowindow.open(map, marker);
          });

          window.kakao.maps.event.addListener(marker, "mouseout", () => {
            infowindow.close();
          });       
        });

        const clusterer = new window.kakao.maps.MarkerClusterer({
          map:map,
          markers:markers,
          averageCenter: true,
          minLevel:5
        })

        window.kakao.maps.event.addListener(map, "zoom_changed", function() {
          const currentLevel = map.getLevel();

          if (currentLevel > 5){
            polyline.setMap(null);
          } else {
            polyline.setMap(map);
          }
        });

        polyline = new window.kakao.maps.Polyline({
          map,
          path: linePath,
          strokeWeight: 5,
          strokeColor: "#0f62fe",
          strokeOpacity: 0.8,
          strokeStyle: "solid",
        });

        if (linePath.length > 0) {
          map.setCenter(linePath[0]);
        }
      });
    };

    document.head.appendChild(script);
  }, [places, kakaoApiKey]);

  return (
    <div
      ref={mapRef} //여기 연결
      style={{ width: "100%", height: "400px", border: "1px solid #ddd" }}
    ></div>
  );
};

export default KakaoMapView;