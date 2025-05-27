# Tweet Fetcher - JavaScript Implementation

Bu proje, Hyperbrowser JavaScript SDK kullanarak Twitter'dan (X) ilk 1000 tweet'i çekmek için geliştirilmiştir.

## 🚀 Özellikler

- **1000 Tweet Hedefi**: Playwright ile akıllı scroll yaparak yaklaşık 1000 tweet çekmeyi hedefler
- **Browser Automation**: Gerçek browser ile etkileşim kurarak doğal davranış sergiler
- **Akıllı Scroll**: Her scroll arası 1.5 saniye bekleyerek bot algısını önler
- **Tweet Counting**: Gerçek zamanlı tweet sayısı takibi
- **Çoklu Format**: Markdown, HTML ve Screenshot formatlarında çıktı
- **Stealth Mode**: Twitter'ın bot algısını atlatmak için özel konfigürasyon
- **Proxy Desteği**: Rate limit riskini azaltır
- **Captcha Çözümü**: Otomatik doğrulama çözümü
- **Hata Yönetimi**: Detaylı hata logları ve geri bildirim
- **Session Management**: Otomatik session cleanup
- **Timestamped Dosyalar**: Her çalıştırmada benzersiz dosya isimleri

## 📋 Gereksinimler

- Node.js (v18 veya üzeri)
- npm veya yarn
- Hyperbrowser API anahtarı ([buradan](https://app.hyperbrowser.ai) alabilirsiniz)
- Playwright (otomatik olarak yüklenecek)

## 🛠️ Kurulum

1. **Bağımlılıkları yükleyin:**
   ```bash
   npm install
   ```

2. **Environment dosyasını oluşturun:**
   ```bash
   cp env.example .env
   ```

3. **API anahtarınızı ekleyin:**
   `.env` dosyasını açın ve API anahtarınızı ekleyin:
   ```env
   HYPERBROWSER_API_KEY=your_hyperbrowser_api_key_here
   ```

## 🏃‍♂️ Kullanım

### Temel Kullanım
```bash
npm start
```

### Development Mode (Auto-reload)
```bash
npm run dev
```

## 📊 Çıktı Dosyaları

Scraping işlemi tamamlandıkında `output/` klasöründe şu dosyalar oluşturulur:

- `tweets_[timestamp].md` - Tweet'ler ve metadata markdown formatında
- `tweets_[timestamp].html` - Tam sayfa HTML içeriği
- `screenshot_[timestamp].png` - Tam sayfa ekran görüntüsü
- `metadata_[timestamp].json` - Scraping metadata ve istatistikler
- `error_[timestamp].json` - Hata durumunda log dosyası

## ⚙️ Konfigürasyon Detayları

### Session Options
- `acceptCookies: false` - Cookie kabul etmez
- `useStealth: true` - Bot algısını zorlaştırır
- `useProxy: true` - Rate limit riskini azaltır
- `solveCaptchas: true` - Otomatik captcha çözümü

### Browser Automation
- `maxScrolls: 100` - Maksimum 100 scroll (≈1000 tweet)
- `scrollDelay: 1500` - Her scroll arası 1.5 saniye bekler
- `tweet counting` - Gerçek zamanlı tweet sayısı takibi
- `smart detection` - Yeni tweet yüklenip yüklenmediğini kontrol eder
- `full page screenshot` - Tam sayfa ekran görüntüsü alır
- `session cleanup` - Otomatik session temizliği

## 📈 Performans Optimizasyonları

1. **Smart Scrolling**: Her scroll'da yaklaşık 10 tweet yüklendiği varsayılarak 100 scroll ile 1000 tweet hedeflenir
2. **Rate Limiting**: Scroll'lar arası bekleme ile Twitter'ın rate limit'ine takılma riski azaltılır
3. **Stealth Mode**: Bot algılamasını zorlaştıran özel konfigürasyon
4. **Proxy Usage**: IP bazlı kısıtlamaları aşmak için proxy kullanımı

## 🔧 Sorun Giderme

### Yaygın Hatalar

1. **API Key Eksik**
   ```
   ❌ HYPERBROWSER_API_KEY environment variable is required!
   ```
   **Çözüm**: `.env` dosyasında API anahtarınızı kontrol edin

2. **Rate Limit**
   ```
   Rate limit exceeded
   ```
   **Çözüm**: Birkaç dakika bekleyip tekrar deneyin

3. **Captcha**
   ```
   Captcha verification required
   ```
   **Çözüm**: `solveCaptchas: true` ayarı zaten aktif, otomatik çözülmelidir

### Debug İpuçları

- Hata durumunda `output/` klasöründe error log dosyası oluşturulur
- Metadata dosyasında scraping detayları bulunur
- Screenshot dosyası sayfanın son halini gösterir

## 🎯 Hedef Kullanıcı

Bu script özellikle aşağıdaki durumlar için tasarlanmıştır:

- Twitter profillerinden büyük miktarda tweet çekmek
- Analiz için tweet verilerini toplamak
- Sosyal medya araştırmaları yapmak
- İçerik analizi için veri toplama

## 📝 Notlar

- Twitter'ın Terms of Service'ini ihlal etmemeye dikkat edin
- Büyük miktarda veri çekerken sorumlu kullanım yapın
- API rate limit'lerini göz önünde bulundurun
- Kişisel verileri işlerken GDPR/KVKK kurallarına uyun

## 🤝 Katkıda Bulunma

Bu projeyi geliştirmek için:

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit edin (`git commit -m 'Add amazing feature'`)
4. Branch'i push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 🔗 Yararlı Linkler

- [Hyperbrowser Docs](https://docs.hyperbrowser.ai)
- [Hyperbrowser SDK](https://www.npmjs.com/package/@hyperbrowser/sdk)
- [API Dashboard](https://app.hyperbrowser.ai) 