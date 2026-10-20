# OPTIK MuJoCo hareket gösterimi

`optik-v1.xml` açık test, `optik-v2.xml` kapalı gövde. STL görselleri CAD'den metreye çevrilmiştir. `simulate.py` konum servolarıyla 10 saniyelik iki eksen hareketi çalıştırır ve MP4/CSV üretir.

**Sınır:** MG996R elektriksel modeli, sürekli dönüş hız haritası, sensör gecikmesi, sürtünme, kablo kuvveti ve kütle/ataletler ölçülmedi. Kullanılan konum aktüatörleri gerçek sürekli dönüşlü servonun kontrol modeli değildir. Kütle/atalet sayıları yaklaşık varsayımdır. Görsel meshlerin çarpışması devre dışıdır; mekanik kesişim kontrolü ayrı CAD raporundadır. Bu dosya kalibre edilmiş dijital ikiz veya fiziksel servo başarım kanıtı değildir.

Kaynak: https://mujoco.readthedocs.io/en/3.2.7/python.html
