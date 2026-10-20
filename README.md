# OPTIK — kamera ve ışık platformu

**R0.2 mühendislik prototipi.** Bambu Lab X1 Carbon için, iki eksenli ve rulmanlı optik laboratuvar platformu. V1 açık test/servis, V2 sökülebilir kapaklı sürümdür. Yalnız kamera ve üreticisinin Sınıf 1 olarak belirttiği küçük optik modül taşır.

![V2 kapalı sürüm](images/montaj-v2.png)
![V1 açık test sürümü](images/montaj.png)
![V2 arka servis](images/montaj-v2-arka.png)
![Elektronik referans yerleşimi](images/elektronik-yerlesim.png)

## Dosyalar

- [38 sayfa A3 teknik PDF](drawings/OPTIK-teknik-cizimler.pdf): üç görünüş, dış ölçüler, kritik delik/pattern ölçüleri ve montaj notları.
- [V1 montaj STEP ZIP](cad/OPTIK-V1-montaj.zip) · [V2 montaj STEP ZIP](cad/OPTIK-V2-montaj.zip).
- `cad/`: 32 düzenlenebilir STEP parçası. `stl/`: baskı yönüne çevrilmiş, Z=0 STL dosyaları.
- [Donanım listesi](BOM.csv) · [Bağlantı bazında M2 vida planı](drawings/vida-plani.csv) · [Temel delik koordinatları](drawings/delik-koordinatlari.csv) · [Eklem referansları](joint-frames.json).
- [Parça kontrolleri](checks/part-checks.json) · [Montaj örneklemesi](checks/assembly-checks.json).
- [MuJoCo V1 videosu](simulation/optik-v1.mp4) · [MuJoCo V2 videosu](simulation/optik-v2.mp4) · [Simülasyon kapsamı](simulation/README.md).

## Mekanik tasarım

Pan ve tilt hedef aralığı ±90°; iki eksende 608 rulman ve mekanik durdurucu vardır. Tilt ekseni Z227 mm. Dişli çifti m1.5, 30/36 diş, 20° basınç açısı, 49.5 mm eksen aralığıdır. Oran 5:6'dır; boşluk ve doğruluk fiziksel prototipte ölçülür.

Montaj bağlantıları M2'dir. Rulman milleri D8, sol tilt mili M8×35 DIN931, sağ tilt omuz mili D8×16/M6 olarak kalır. Uzun M2 vidaların baş/diş zinciri ve rijitliği fiziksel montajda kontrol edilmelidir. Insert siparişi, seçilen üreticinin delik ölçüsü ve P24 kuponu görülerek kesinleştirilir.

V2 alt kabuk yaklaşık 205×165 mm; tüm parça STL'leri nominal 256³ mm X1 Carbon hacmine göre kontrol edilir. Başlangıç: PETG, üreticinin profili, 0.4 mm nozül, 0.20 mm katman, 5 duvar, 6 üst/alt ve %30 dolgu. Dikmeler/yan çıkıntılar yerel destek ister. Önce P24 geçme kuponu, sonra tek eklem prototipi basılmalıdır. Dilimleyici önizlemesi ve gerçek baskı yapılmadı.

## Elektronik ve kablo yolları

ESP başlığın P06 sırtında P25 kasetiyle taşınır; kamera DVP bağlantısı kısa tutulur. Referans kart, **ESP32-S3 DevKitC-1 62.74×25.40 mm** dış ölçüsüne göre görselleştirilmiştir. N16R8 bellek çeşididir; kullanıcının PCB modeli henüz doğrulanmadı. Gösterilen servo/PCB/USB geometrileri boyutsal referans zarflarıdır, üretici orijinal CAD'i değildir. Kullanıcının kartı ve servo varyantı ölçülmeden birebir uyum sözü verilemez.

P16 altındaki kanallar 12 mm genişlik, 4.5 mm derinlik; ayak geçişleri D8.5 mm'dir. Pan flanşı altında R22–44 mm çevresinde servis halkası için boşluk bırakıldı. Esnek, ince demet ve başlangıçta en az 15 mm bükülme yarıçapı hedeflenir. Gerçek kablo geometrisi/hareket testi henüz yapılmadı. Arka USB-C panel #4218 ile programlama erişimi, ayrı D10 güç geçişi vardır. 30 cm panel kablosuna ek uzatma ve kart ucunda ince köşe fişi gerekebilir; fiş çakışmaları gerçek kartla doğrulanır.

Kullanıcının 360° diye satın aldığı üç kablolu MG996R, sürekli dönüşlü kabul edildi. Üç kablo açı telemetrisi sağlamaz; iki AS5600 geri bildirimi korunur. Sensörlerin I2C adresi aynı olduğundan iki ayrı I2C hattı veya çoklayıcı gerekir. Servolar ayrı regüle kaynakla beslenir, ESP ile GND ortaktır. L298N RC servo sürücüsü olarak kullanılmaz. Kesin GPIO ataması ve firmware bu CAD paketine dahil değildir.

## Kontrollerin sınırı

Üretim betikleri her STEP için tek geçerli katı; her STL için kapalı ağ, pozitif hacim, Z=0 ve baskı hacmi kontrolü uygular. Montaj kontrolü nötr konum, seçili tilt açıları, pan durdurucuları ve dişli temasını örnekler. Sonuçlar JSON raporlarındadır. Tüm vida/fiş başları, sürekli çarpışma, kablo kuvvetleri, dayanım, termal davranış, optik hizalama ve gerçek donanım uyumu bu raporlarla kanıtlanmaz.

MuJoCo XML modelleri CAD görsellerini SI birimleriyle kullanır; kütle/ataletler ve konum aktüatörleri yaklaşık gösterim parametreleridir. Gerçek MG996R sürekli dönüş kontrolü ve elektriksel davranışı modellenmedi. Video bir hareket gösterimidir; kalibre edilmiş dijital ikiz veya donanım başarım testi değildir. [Simülasyon raporu](simulation/simulation-report.json) ve eklem CSV'leri tekrar üretilebilir.

Delik CSV'si temel dairesel delik/pattern merkezlerini **parçanın STEP koordinatlarında** verir; döndürülmüş STL koordinatlarında değildir. P03–P08 ve P25 montajda Z227 mm taşınır. Slotlar, cepler ve yüzeyler için STEP esastır. PDF prototip teknik pakettir; alüminyum imalatı için eksiksiz GD&T/tolerans onayı değildir.

## Alüminyum revizyonu

FDM kabuklarını doğrudan CNC'ye göndermek yerine köprü/dikmeler düz plaka ve ara parçalarla yeniden tasarlanmalıdır. Metal yatak geçmeleri, M2 diş/vida taşıma kapasitesi, kütle/atalet, servo yeterliliği ve ESP anten açıklığı yeniden değerlendirilir. Mevcut STEP'ler revizyon başlangıcıdır; metal üretim onayı verilmedi.

## Yeniden üretim

`pip install -r requirements-ci.txt`, ardından sırasıyla `python model.py`, `python validate.py`, `python documents.py`, `python publish.py`, `python prepare_simulation.py`, `python simulate.py`. Linux video için `libosmesa6` gerekir. GitHub Actions'taki **Build CAD and MuJoCo previews** iş akışı aynı adımları çalıştırır. PDF ve video ancak bu akış başarıyla tamamlandıktan sonra sürüme alınır.

## Üretici kaynakları

- [Tower Pro MG996R](https://towerpro.com.tw/product/mg996R/): gövde ölçüleri ve sürüm bilgileri. Mevcut 360° varyant ayrıca doğrulanmalıdır.
- [Waveshare OV5640 Board A](https://www.waveshare.com/product/modules/cameras-audio-video/cameras/ov5640-camera-board-a.htm): 35.7×23.9 mm PCB, 5 MP, DVP. Azami çözünürlük hızlı kare hızı garantisi değildir.
- [Espressif kamera sürücüsü](https://github.com/espressif/esp32-camera) · [DevKitC-1 resmi ölçü çizimi](https://dl.espressif.com/dl/PCB_ESP32-S3-DevKitC-1_V1_20210312CB.pdf).
- [Picotronic DI650-0.4-3(8x21)](https://www.picotronic.de/picopage/en/product/detail/id/1934/category/3): Ø8×21 mm, 650 nm, 0.4 mW, üreticinin Class 1 sınıflandırması. Tam cihaz sınıfı ayrıca değerlendirilir.
- [Adafruit AS5600 PCB](https://github.com/adafruit/Adafruit-AS5600-Magnetic-Angle-Sensor-PCB): 25.4×17.78 mm kart, 20.32×12.70 mm delik aralığı yayımlanan Eagle dosyasından çıkarılmıştır; PCB dosyası yeniden dağıtılmıyor.
- [AS5600 kılavuzu](https://learn.adafruit.com/adafruit-as5600-magnetic-angle-sensor) · [USB-C panel #4218](https://www.adafruit.com/product/4218).
- [Bambu Lab X1 Carbon teknik özellikleri](https://public-cdn.bambulab.com/store/bambulab-X1-carbon-tech-specs.pdf?v=20241214042009) · [MuJoCo Python API](https://mujoco.readthedocs.io/en/3.2.7/python.html).

## Parça galerisi

Her görsel gerçek CAD geometrisinden üretilmiştir. P13 iki, P26 altı adet; P24 test kuponu, P26 isteğe bağlıdır. E parçaları yalnız V2 içindir.

### P01 - Elektronik taban

190 x 150 x 30 mm / 3 mm duvar / 6 mm taban

![Elektronik taban](images/P01.png)

[STEP](cad/P01.step) · [STL](stl/P01.stl) · [Ölçülü çizim](drawings/sayfa-07.png)

### P02 - Servis kapagi

190 x 150 x 3 mm / sokulebilir / kablo ve havalandirma acikliklari

![Servis kapagi](images/P02.png)

[STEP](cad/P02.step) · [STL](stl/P02.stl) · [Ölçülü çizim](drawings/sayfa-08.png)

### P03 - Optik baslik govdesi

OV5640 + D8 mm Class 1 isik modulu / yalniz optik yuk

![Optik baslik govdesi](images/P03.png)

[STEP](cad/P03.step) · [STL](stl/P03.stl) · [Ölçülü çizim](drawings/sayfa-09.png)

### P04 - Kamera kaseti

Waveshare OV5640 Board A / 36.1 x 24.3 mm PCB oturma cebi

![Kamera kaseti](images/P04.png)

[STEP](cad/P04.step) · [STL](stl/P04.stl) · [Ölçülü çizim](drawings/sayfa-10.png)

### P05 - Kamera baski cercevesi

1.5 mm baski cercevesi / 0.5 mm ince kopuk ara katman

![Kamera baski cercevesi](images/P05.png)

[STEP](cad/P05.step) · [STL](stl/P05.stl) · [Ölçülü çizim](drawings/sayfa-11.png)

### P06 - Elektronik sirt kapagi

Kisa kamera baglantisi / ESP kaseti / 4 adet M2 vida

![Elektronik sirt kapagi](images/P06.png)

[STEP](cad/P06.step) · [STL](stl/P06.stl) · [Ölçülü çizim](drawings/sayfa-12.png)

### P07 - Isik alt yatagi

Picotronic D8 x 21 mm govde / D8.30 yatak

![Isik alt yatagi](images/P07.png)

[STEP](cad/P07.step) · [STL](stl/P07.stl) · [Ölçülü çizim](drawings/sayfa-13.png)

### P08 - Isik ust kelepcesi

Iki M2 ile kapatma / optik govdeye baskiyi sinirla

![Isik ust kelepcesi](images/P08.png)

[STEP](cad/P08.step) · [STL](stl/P08.stl) · [Ölçülü çizim](drawings/sayfa-14.png)

### P09 - Pan rulman kulesi

608 yatak / enkoder erisimi / 4 adet M2 taban baglantisi

![Pan rulman kulesi](images/P09.png)

[STEP](cad/P09.step) · [STL](stl/P09.stl) · [Ölçülü çizim](drawings/sayfa-15.png)

### P10 - Ust rulman kartusu

Ikinci 608 rulman / iki yatak arasinda 12 mm merkez mesafesi

![Ust rulman kartusu](images/P10.png)

[STEP](cad/P10.step) · [STL](stl/P10.stl) · [Ölçülü çizim](drawings/sayfa-16.png)

### P11 - Pan enkoder cekmecesi

Adafruit AS5600 #6357 / uretici PCB deliklerine gore

![Pan enkoder cekmecesi](images/P11.png)

[STEP](cad/P11.step) · [STL](stl/P11.stl) · [Ölçülü çizim](drawings/sayfa-17.png)

### P12 - Pan servo sehpası

MG996R govde oturma acikligi / uzun montaj delikleri

![Pan servo sehpası](images/P12.png)

[STEP](cad/P12.step) · [STL](stl/P12.stl) · [Ölçülü çizim](drawings/sayfa-18.png)

### P13 - Servo tahrik dislisi

30 dis / modul 1.5 / 20 derece / stok servo hornuna vidalanir

![Servo tahrik dislisi](images/P13.png)

[STEP](cad/P13.step) · [STL](stl/P13.stl) · [Ölçülü çizim](drawings/sayfa-19.png)

### P14 - Pan cikis dislisi

36 dis / 49.5 mm eksen araligi / cikis hiz orani 5:6

![Pan cikis dislisi](images/P14.png)

[STEP](cad/P14.step) · [STL](stl/P14.stl) · [Ölçülü çizim](drawings/sayfa-20.png)

### P15 - Pan doner tasiyici

D8 mil sikma gobegi / korumali kablo halkasi / 20 mm ek aciklik

![Pan doner tasiyici](images/P15.png)

[STEP](cad/P15.step) · [STL](stl/P15.stl) · [Ölçülü çizim](drawings/sayfa-21.png)

### P16 - Optik platform koprusu

168 x 90 x 8 mm / altta 12 mm kablo kanallari

![Optik platform koprusu](images/P16.png)

[STEP](cad/P16.step) · [STL](stl/P16.stl) · [Ölçülü çizim](drawings/sayfa-22.png)

### P17 - Sol hareket dikmesi

Tilt servosu + 608 yatagi / yan yuzeyi baski tablasina

![Sol hareket dikmesi](images/P17.png)

[STEP](cad/P17.step) · [STL](stl/P17.stl) · [Ölçülü çizim](drawings/sayfa-23.png)

### P18 - Sag sensor dikmesi

608 yatak / AS5600 sabit montaji / +-90 derece durdurucular

![Sag sensor dikmesi](images/P18.png)

[STEP](cad/P18.step) · [STL](stl/P18.stl) · [Ölçülü çizim](drawings/sayfa-24.png)

### P19 - Tilt cikis dislisi

36 dis / M8 x 35 DIN931 baslik cebi

![Tilt cikis dislisi](images/P19.png)

[STEP](cad/P19.step) · [STL](stl/P19.stl) · [Ölçülü çizim](drawings/sayfa-25.png)

### P20 - Pan aktarim muhafazasi

Dislileri orter / iki mekanik durdurucu / kapak asagi basilir

![Pan aktarim muhafazasi](images/P20.png)

[STEP](cad/P20.step) · [STL](stl/P20.stl) · [Ölçülü çizim](drawings/sayfa-26.png)

### P21 - Pan miknatis adaptoru

Cap boyunca kutuplanmis D6 x 2.5 miknatis / mile yapistirma

![Pan miknatis adaptoru](images/P21.png)

[STEP](cad/P21.step) · [STL](stl/P21.stl) · [Ölçülü çizim](drawings/sayfa-27.png)

### P22 - Tilt miknatis adaptoru

D8 omuz civatasi basligina gecme / D6 x 2.5 capsal miknatis

![Tilt miknatis adaptoru](images/P22.png)

[STEP](cad/P22.step) · [STL](stl/P22.stl) · [Ölçülü çizim](drawings/sayfa-28.png)

### P23 - Enkoder dis kapagi

AS5600 PCB arka yuzu / 4 adet M2 baglanti

![Enkoder dis kapagi](images/P23.png)

[STEP](cad/P23.step) · [STL](stl/P23.stl) · [Ölçülü çizim](drawings/sayfa-29.png)

### P24 - Gecme deneme kuponu

Ilk baski / rulman, mil, optik modul ve insert toleransi

![Gecme deneme kuponu](images/P24.png)

[STEP](cad/P24.step) · [STL](stl/P24.stl) · [Ölçülü çizim](drawings/sayfa-30.png)

### P25 - ESP elektronik kaseti

62.74 x 25.40 mm DevKitC-1 referansi / ayarlanabilir baglama

![ESP elektronik kaseti](images/P25.png)

[STEP](cad/P25.step) · [STL](stl/P25.stl) · [Ölçülü çizim](drawings/sayfa-31.png)

### P26 - Kablo kilavuz klipsi

Genel M2 kablo rehberi / prototipte uygun konuma takilir

![Kablo kilavuz klipsi](images/P26.png)

[STEP](cad/P26.step) · [STL](stl/P26.stl) · [Ölçülü çizim](drawings/sayfa-32.png)

### E01 - V2 taban on kabuk

Sokulebilir optik platform dis kabugu / R0.2 / M2 montaj

![V2 taban on kabuk](images/E01.png)

[STEP](cad/E01.step) · [STL](stl/E01.stl) · [Ölçülü çizim](drawings/sayfa-33.png)

### E02 - V2 taban arka kabuk

Sokulebilir optik platform dis kabugu / R0.2 / M2 montaj

![V2 taban arka kabuk](images/E02.png)

[STEP](cad/E02.step) · [STL](stl/E02.stl) · [Ölçülü çizim](drawings/sayfa-34.png)

### E03 - V2 sol sabit cerceve

Sokulebilir optik platform dis kabugu / R0.2 / M2 montaj

![V2 sol sabit cerceve](images/E03.png)

[STEP](cad/E03.step) · [STL](stl/E03.stl) · [Ölçülü çizim](drawings/sayfa-35.png)

### E04 - V2 sol servis kapagi

Sokulebilir optik platform dis kabugu / R0.2 / M2 montaj

![V2 sol servis kapagi](images/E04.png)

[STEP](cad/E04.step) · [STL](stl/E04.stl) · [Ölçülü çizim](drawings/sayfa-36.png)

### E05 - V2 sag sabit cerceve

Sokulebilir optik platform dis kabugu / R0.2 / M2 montaj

![V2 sag sabit cerceve](images/E05.png)

[STEP](cad/E05.step) · [STL](stl/E05.stl) · [Ölçülü çizim](drawings/sayfa-37.png)

### E06 - V2 sag servis kapagi

Sokulebilir optik platform dis kabugu / R0.2 / M2 montaj

![V2 sag servis kapagi](images/E06.png)

[STEP](cad/E06.step) · [STL](stl/E06.stl) · [Ölçülü çizim](drawings/sayfa-38.png)
