# OPTIK - Kamera ve ışık platformu

İki eksenli, açı geri bildirimli laboratuvar optik platformu. Kamera ve üreticisi tarafından Sınıf 1 olarak sınıflandırılmış küçük bir ışık modülü taşır.

**Durum: R0.1 mühendislik prototipi.** Parça geometrileri oluşturulmuştur. Fiziksel montaj, baskı toleransları, servo varyantı, sensör alan şiddeti ve kablo hareketi henüz gerçek donanımla doğrulanmamıştır. Montaj ve hareket kontrolleri üzerinde çalışma sürüyor. Bu dosyalar seri üretim onayı değildir.

![İlk montaj görünümü](images/montaj.png)

## Dosyalar

- `cad/`: Düzenlenebilir STEP parçaları ve montaj.
- `stl/`: Baskı yönüne çevrilmiş, tabla düzlemine oturtulmuş STL parçaları. P13 iki adet basılır.
- `images/`: Gerçek CAD geometrisinden üretilmiş parça görselleri; yapay görsel üretimi kullanılmadı.
- `drawings/`: Ölçülü teknik çizimler hazırlanıyor.
- `checks/`: Geometri ve montaj kontrolleri hazırlanıyor.
- `parts.json`: Parça ölçüleri, adetler, hacimler, baskı yönleri ve kontrol sonuçları.
- `model.py`, `geometry.py`, `render.py`: Parametrik üretim kaynağı.

## Tasarım esasları

- Baskı cihazı: Bambu Lab X1 Carbon. Nominal hacim 256 × 256 × 256 mm. En büyük temel parça 190 × 150 mm.
- Pan ve tilt için mekanik hedef aralık: ±90°. Gerçek hareket açıklığı montaj testinde doğrulanacak.
- Kullanıcının servo bilgisi: MG996R, 360° olarak satılmış. Sürekli dönüşlü sürüm varsayılmıştır; açı, iki AS5600 ile ölçülecek. Hız komutunu açı komutu gibi kullanmak doğru değildir.
- 30/36 dişli çifti, modül 1.5, 20° basınç açısı, 49.5 mm eksen aralığı. Çıkış açısal hızı servo hızının 5/6'sı; bu oran bir doğruluk garantisi değildir.
- 608 rulmanlar ve 8 mm miller, yükün yalnız servo miline binmesini önlemek için kullanılır.
- N16R8 ifadesi ESP32-S3 kartının PCB ölçüsü değildir. Bilinmeyen kart deliklerini varsaymak yerine elektronik tabanda bağlama delikleri bırakıldı.
- Ek donanım: iki AS5600 kartı, uygun çap boyunca kutuplanmış mıknatıslar, rulmanlar, miller, bağlantı elemanları ve ayrı servo beslemesi gerekir. Mevcut üç L298N, standart RC servo sürücüsü yerine geçmez.
- Kamera adayının 5 MP değeri sensörün azami çözünürlüğüdür; aynı çözünürlükte yüksek kare hızı veya hızlı hedef takibi vaat edilmez. DVP bağlantısı ve pin bütçesi kart modeline göre doğrulanmalıdır.

## Doğrulanmış üretici kaynakları

- [Tower Pro MG996R](https://towerpro.com.tw/product/mg996R/): gövde ölçüleri, gerilim ve sürüm farklılıkları. Üretici standart MG996R için 159° belirtir; 360° sürekli dönüşlü varyantı ayrıca ele alır.
- [Waveshare OV5640 Board A](https://www.waveshare.com/product/modules/cameras-audio-video/cameras/ov5640-camera-board-a.htm): 35.7 × 23.9 mm PCB, 5 MP, DVP.
- [Espressif kamera sürücüsü](https://github.com/espressif/esp32-camera): ESP32-S3 ve OV5640 sensör desteği. Sensör desteği, her kartın mekanik veya pin bağlantısının aynı olduğu anlamına gelmez.
- [Picotronic DI650-0.4-3(8x21)](https://www.picotronic.de/picopage/en/product/detail/id/1934/category/3): 650 nm, 0.4 mW, Ø8 × 21 mm, üretici sınıflandırması Class 1. Tüm cihazın güvenlik sınıfı, tek modülün sınıfından otomatik olarak türetilmez.
- [Adafruit AS5600 PCB](https://github.com/adafruit/Adafruit-AS5600-Magnetic-Angle-Sensor-PCB): 25.4 × 17.78 mm kart; delik merkezleri 20.32 × 12.70 mm. Ölçüler yayımlanan Eagle dosyasından çıkarıldı. PCB dosyası burada yeniden dağıtılmıyor.
- [Adafruit AS5600 kullanım kılavuzu](https://learn.adafruit.com/adafruit-as5600-magnetic-angle-sensor): manyetik açı algılama ve bağlantı.
- [Bambu Lab X1 Carbon teknik özellikleri](https://public-cdn.bambulab.com/store/bambulab-X1-carbon-tech-specs.pdf?v=20241214042009).

## Parça galerisi

Her görselin başındaki P numarası, aynı numaralı STEP ve STL dosyasına karşılık gelir. Henüz baskı veya gerçek donanım testi yapılmadı.

### P01 - Elektronik taban

190 x 150 x 30 mm / 3 mm duvar / 6 mm taban

![Elektronik taban](images/P01.png)

[STEP](cad/P01.step) · [STL](stl/P01.stl)

### P02 - Servis kapagi

190 x 150 x 3 mm / sokulebilir / kablo ve havalandirma acikliklari

![Servis kapagi](images/P02.png)

[STEP](cad/P02.step) · [STL](stl/P02.stl)

### P03 - Optik baslik govdesi

OV5640 + D8 mm Class 1 isik modulu / yalniz optik yuk

![Optik baslik govdesi](images/P03.png)

[STEP](cad/P03.step) · [STL](stl/P03.stl)

### P04 - Kamera kaseti

Waveshare OV5640 Board A / 36.1 x 24.3 mm PCB oturma cebi

![Kamera kaseti](images/P04.png)

[STEP](cad/P04.step) · [STL](stl/P04.stl)

### P05 - Kamera baski cercevesi

1.5 mm baski cercevesi / 0.5 mm ince kopuk ara katman

![Kamera baski cercevesi](images/P05.png)

[STEP](cad/P05.step) · [STL](stl/P05.stl)

### P06 - Baslik arka kapagi

Kablo cikisi + sogutma / 4 adet M3 vida

![Baslik arka kapagi](images/P06.png)

[STEP](cad/P06.step) · [STL](stl/P06.stl)

### P07 - Isik alt yatagi

Picotronic D8 x 21 mm govde / D8.30 yatak

![Isik alt yatagi](images/P07.png)

[STEP](cad/P07.step) · [STL](stl/P07.stl)

### P08 - Isik ust kelepcesi

Iki M2.5 ile kapatma / optik govdeye baskiyi sinirla

![Isik ust kelepcesi](images/P08.png)

[STEP](cad/P08.step) · [STL](stl/P08.stl)

### P09 - Pan rulman kulesi

608 yatak / enkoder erisimi / 4 adet M4 taban baglantisi

![Pan rulman kulesi](images/P09.png)

[STEP](cad/P09.step) · [STL](stl/P09.stl)

### P10 - Ust rulman kartusu

Ikinci 608 rulman / iki yatak arasinda 12 mm merkez mesafesi

![Ust rulman kartusu](images/P10.png)

[STEP](cad/P10.step) · [STL](stl/P10.stl)

### P11 - Pan enkoder cekmecesi

Adafruit AS5600 #6357 / uretici PCB deliklerine gore

![Pan enkoder cekmecesi](images/P11.png)

[STEP](cad/P11.step) · [STL](stl/P11.stl)

### P12 - Pan servo sehpası

MG996R govde oturma acikligi / uzun montaj delikleri

![Pan servo sehpası](images/P12.png)

[STEP](cad/P12.step) · [STL](stl/P12.stl)

### P13 - Servo tahrik dislisi

30 dis / modul 1.5 / 20 derece / stok servo hornuna vidalanir

![Servo tahrik dislisi](images/P13.png)

[STEP](cad/P13.step) · [STL](stl/P13.stl)

### P14 - Pan cikis dislisi

36 dis / 49.5 mm eksen araligi / cikis hiz orani 5:6

![Pan cikis dislisi](images/P14.png)

[STEP](cad/P14.step) · [STL](stl/P14.stl)

### P15 - Pan doner tasiyici

D8 mil sikma gobegi / kamera koprusu / mekanik hareket durdurucu

![Pan doner tasiyici](images/P15.png)

[STEP](cad/P15.step) · [STL](stl/P15.stl)

### P16 - Optik platform koprusu

168 x 90 x 6 mm / iki dikme / yalniz kamera ve isik basligi

![Optik platform koprusu](images/P16.png)

[STEP](cad/P16.step) · [STL](stl/P16.stl)

### P17 - Sol hareket dikmesi

Tilt servosu + 608 yatagi / yan yuzeyi baski tablasina

![Sol hareket dikmesi](images/P17.png)

[STEP](cad/P17.step) · [STL](stl/P17.stl)

### P18 - Sag sensor dikmesi

608 yatak / AS5600 sabit montaji / +-90 derece durdurucular

![Sag sensor dikmesi](images/P18.png)

[STEP](cad/P18.step) · [STL](stl/P18.stl)

### P19 - Tilt cikis dislisi

36 dis / M8 baslik yakalama / standart 8 mm omuzlu baglanti

![Tilt cikis dislisi](images/P19.png)

[STEP](cad/P19.step) · [STL](stl/P19.stl)

### P20 - Pan aktarim muhafazasi

Dislileri orter / iki mekanik durdurucu / kapak asagi basilir

![Pan aktarim muhafazasi](images/P20.png)

[STEP](cad/P20.step) · [STL](stl/P20.stl)

### P21 - Pan miknatis adaptoru

Cap boyunca kutuplanmis D6 x 2.5 miknatis / mile yapistirma

![Pan miknatis adaptoru](images/P21.png)

[STEP](cad/P21.step) · [STL](stl/P21.stl)

### P22 - Tilt miknatis adaptoru

D8 omuz civatasi basligina gecme / D6 x 2.5 capsal miknatis

![Tilt miknatis adaptoru](images/P22.png)

[STEP](cad/P22.step) · [STL](stl/P22.stl)

### P23 - Enkoder dis kapagi

AS5600 PCB arka yuzu / 4 adet M2.5 baglanti

![Enkoder dis kapagi](images/P23.png)

[STEP](cad/P23.step) · [STL](stl/P23.stl)

