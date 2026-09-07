# Character Consistency Audit — recurring persons with multiple sheets

_Registry: 846 entries • 68 recurring persons detected • 68 rendered with 2+ distinct character sheets • 12 with a real skin/age drift._

Each historical person who appears in several stories got a **separate character sheet per story**, so their look can drift. Flags compare the canonical (standalone) description with each per-story one:
- ⚠️ = **real divergence** (skin tone off by ≥2 steps on a fair→black scale, or apparent age off by ≈20+ years) — priority to reconcile.
- · = minor word-choice / life-stage difference (1 tone step or ~10 years) — usually fine.

Age gaps can be legitimate when a story shows the person earlier in life; skin-tone gaps of ≥2 steps are the clearest art-consistency faults.

## Priority reconciliation list

| Person | Canonical sheet | Sheets | ⚠️ entries |
|---|---|---:|---:|
| Sher Shah Suri | `sher_shah_suri` | 10 | 3 |
| Alauddin Khalji | `alauddin_khalji` | 4 | 2 |
| Babur | `babur` | 4 | 2 |
| Rani Durgavati | `rani_durgavati` | 5 | 1 |
| Akka Mahadevi | `akka_mahadevi` | 3 | 1 |
| Banda Singh Bahadur | `banda_singh_bahadur` | 2 | 1 |
| Malik Kafur | `malik_kafur` | 2 | 1 |
| Jamyang Namgyal | `jamyang_namgyal` | 2 | 1 |
| Tailapa II of the Western Chalukyas | `tailapa_ii` | 2 | 1 |
| Sikandar Shah (Sikandar But-Shikan) | `sikandar_shah` | 2 | 1 |
| Durlabhavardhana of Kashmir | `durlabhavardhana` | 2 | 1 |
| Chashtana | `chashtana` | 2 | 1 |

## Detailed breakdown

### Sher Shah Suri  
`canonical: sher_shah_suri`  

- **Canonical sheet:** `assets/_characters/sher_shah_suri/sheet.png`
- **Canonical look:** age=`?`, skin=`wheatish`
- **Appears in 10 entries:**
    - `sher_shah_suri_and_rao_maldev_rathore` (age=?, skin=brown)  · skin wheatish→brown
    - `sher_shah_suri_and_humayun` (age=late-30s, skin=light-brown)
    - `sher_shah_suri_and_rao_maldeo_rathore` (age=?, skin=dark)  ⚠️ SKIN wheatish→dark
    - `sher_shah_suri_and_shahu_sultan` (age=?, skin=wheatish)
    - `sher_shah_suri_and_the_patwari` (age=?, skin=wheatish-brown)  · skin wheatish→wheatish-brown
    - `sher_shah_suri_and_the_dak_runners` (age=?, skin=wheatish)
    - `sher_shah_suri_and_khawas_khan_marwat` (age=?, skin=black)  ⚠️ SKIN wheatish→black
    - `sher_shah_suri_and_puran_mal` (age=?, skin=dark)  ⚠️ SKIN wheatish→dark
    - `nasiruddin_nasrat_shah_sher_shah_suri_and_humayu` (age=mid-40s, skin=wheatish)

### Rani Durgavati  
`canonical: rani_durgavati`  

- **Canonical sheet:** `assets/_characters/rani_durgavati/sheet.png`
- **Canonical look:** age=`early-30s`, skin=`wheatish-brown`
- **Appears in 5 entries:**
    - `rani_durgavati_and_asaf_khan` (age=early-30s, skin=medium-brown)
    - `dalpat_shah_and_rani_durgavati` (age=20s, skin=black)  ⚠️ SKIN wheatish-brown→black
    - `rani_durgavati_and_baz_bahadur` (age=?, skin=medium-brown)
    - `rani_durgavati_and_adhar_kayastha` (age=?, skin=brown)

### Bhoja of Dhara  
`canonical: bhoja_of_dhara`  

- **Canonical sheet:** `assets/_characters/bhoja_of_dhara/sheet.png`
- **Canonical look:** age=`mid-30s`, skin=`wheatish`
- **Appears in 4 entries:**
    - `bhoja_of_dhara_and_the_bhojpur_masons` (age=late-30s, skin=wheatish-brown)  · skin wheatish→wheatish-brown
    - `bhoja_and_the_paramara_administrators` (age=mid-30s, skin=medium-brown)  · skin wheatish→medium-brown
    - `bhoja_and_the_scholars_of_dhar` (age=mid-40s, skin=medium-brown)  · skin wheatish→medium-brown; age mid-30s→mid-40s

### Alauddin Khalji  
`canonical: alauddin_khalji`  

- **Canonical sheet:** `assets/_characters/alauddin_khalji/sheet.png`
- **Canonical look:** age=`mid-40s`, skin=`wheatish`
- **Appears in 4 entries:**
    - `alauddin_khalji_and_ratnasimha` (age=?, skin=dark)  ⚠️ SKIN wheatish→dark
    - `sitaladeva_songara_and_alauddin_khalji` (age=?, skin=dark)  ⚠️ SKIN wheatish→dark
    - `alauddin_khalji_and_ramachandra_yadava` (age=late-20s, skin=wheatish)  · age mid-40s→late-20s

### Malik Ambar  
`canonical: malik_ambar`  

- **Canonical sheet:** `assets/_characters/malik_ambar/sheet.png`
- **Canonical look:** age=`?`, skin=`deep-brown`
- **Appears in 4 entries:**
    - `malik_ambar_and_maloji_bhosale` (age=mid-50s, skin=deep-brown)
    - `malik_ambar_and_deccan_revenue_officers` (age=late-40s, skin=medium-brown)  · skin deep-brown→medium-brown
    - `jahangir_and_malik_ambar` (age=?, skin=dark-brown)

### Babur  
`canonical: babur`  

- **Canonical sheet:** `assets/_characters/babur/sheet.png`
- **Canonical look:** age=`early-40s`, skin=`dark-brown`
- **Appears in 4 entries:**
    - `babur_and_rana_sanga` (age=mid-30s, skin=brown)  · skin dark-brown→brown
    - `babur_and_mahmud_lodi` (age=?, skin=fair)  ⚠️ SKIN dark-brown→fair
    - `babur_and_medini_rai` (age=late-30s, skin=wheatish)  ⚠️ SKIN dark-brown→wheatish

### Jalal-ud-din Muhammad Akbar  
`canonical: akbar`  

- **Canonical sheet:** `assets/_characters/akbar/sheet.png`
- **Canonical look:** age=`late-20s`, skin=`light-brown`
- **Appears in 4 entries:**
    - `akbar_and_man_singh` (age=?, skin=?)
    - `hemu_bairam_khan_and_akbar` (age=?, skin=bronze)  · skin light-brown→bronze
    - `akbar_jaimal_and_patta` (age=?, skin=?)

### Jalaluddin Muhammad Shah  
`canonical: jalaluddin_muhammad_shah`  

- **Canonical sheet:** `assets/_characters/jalaluddin_muhammad_shah/sheet.png`
- **Canonical look:** age=`?`, skin=`medium-brown`
- **Appears in 3 entries:**
    - `jalaluddin_muhammad_shah_and_ma_huan` (age=?, skin=brown)
    - `raja_ganesha_and_jalaluddin_muhammad_shah` (age=?, skin=brown)

### Akka Mahadevi  
`canonical: akka_mahadevi`  

- **Canonical sheet:** `assets/_characters/akka_mahadevi/sheet.png`
- **Canonical look:** age=`?`, skin=`brown`
- **Appears in 3 entries:**
    - `basavanna_akka_mahadevi_and_allama_prabhu` (age=?, skin=brown)
    - `akka_mahadevi_basavanna_and_harihara` (age=?, skin=pale)  ⚠️ SKIN brown→pale

### Narasimhadeva I  
`canonical: narasimhadeva_i`  

- **Canonical sheet:** `assets/_characters/narasimhadeva_i/sheet.png`
- **Canonical look:** age=`?`, skin=`wheatish`
- **Appears in 3 entries:**
    - `narasimhadeva_i_and_tughril_tughan_khan` (age=mid-30s, skin=medium-brown)  · skin wheatish→medium-brown
    - `narasimhadeva_i_and_the_konark_sthapatis` (age=?, skin=medium-brown)  · skin wheatish→medium-brown

### Marthanda Varma (Young Prince)  
`canonical: marthanda_varma`  

- **Canonical sheet:** `assets/_characters/marthanda_varma/sheet.png`
- **Canonical look:** age=`?`, skin=`medium-brown`
- **Appears in 3 entries:**
    - `marthanda_varma_and_the_ettuveetil_pillamar` (age=?, skin=brown)
    - `marthanda_varma_and_ramayyan_dalawa` (age=?, skin=medium-brown)

### Kapilendra Deva  
`canonical: kapilendra_deva`  

- **Canonical sheet:** `assets/_characters/kapilendra_deva/sheet.png`
- **Canonical look:** age=`mid-40s`, skin=`medium-brown`
- **Appears in 3 entries:**
    - `kapilendra_deva_and_hamvira_deva` (age=late-20s, skin=medium-brown)  · age mid-40s→late-20s
    - `kapilendra_deva_and_odishan_silpis` (age=?, skin=brown)

### Menander I (Milinda)  
`canonical: menander_i`  

- **Canonical sheet:** `assets/_characters/menander_i/sheet.png`
- **Canonical look:** age=`mid-30s`, skin=`olive`
- **Appears in 3 entries:**
    - `pushyamitra_shunga_and_menander_i` (age=?, skin=wheatish)
    - `menander_i_and_nagasena` (age=?, skin=olive)

### Nagabhata I  
`canonical: nagabhata_i`  

- **Canonical sheet:** `assets/_characters/nagabhata_i/sheet.png`
- **Canonical look:** age=`early-30s`, skin=`medium-brown`
- **Appears in 3 entries:**
    - `nagabhata_i_and_avanijanashraya_pulakesiraja` (age=?, skin=wheatish-brown)
    - `nagabhata_i_and_avanijanashraya_pulakeshin` (age=mid-30s, skin=dusky)

### Harsha of Kannauj  
`canonical: harsha`  

- **Canonical sheet:** `assets/_characters/harsha/sheet.png`
- **Canonical look:** age=`?`, skin=`wheatish`
- **Appears in 3 entries:**
    - `harsha_vardhana_and_shashanka` (age=?, skin=wheatish)
    - `harsha_and_the_nalanda_stewards` (age=?, skin=medium-brown)  · skin wheatish→medium-brown

### Bahadur Shah Zafar  
`canonical: bahadur_shah_zafar`  

- **Canonical sheet:** `assets/_characters/bahadur_shah_zafar/sheet.png`
- **Canonical look:** age=`?`, skin=`brown`
- **Appears in 2 entries:**
    - `mirza_ghalib_and_bahadur_shah_zafar` (age=?, skin=dark)  · skin brown→dark

### Rajaraja Chola I  
`canonical: rajaraja_chola_i`  

- **Canonical sheet:** `assets/_characters/rajaraja_chola_i/sheet.png`
- **Canonical look:** age=`?`, skin=`medium-brown`
- **Appears in 2 entries:**
    - `rajaraja_chola_i_and_rakkasa_ganga` (age=mid-40s, skin=brown)

### Chandragupta II Vikramaditya  
`canonical: chandragupta_ii_vikramaditya`  

- **Canonical sheet:** `assets/_characters/chandragupta_ii_vikramaditya/sheet.png`
- **Canonical look:** age=`early-30s`, skin=`medium-brown`
- **Appears in 2 entries:**
    - `chandragupta_ii_vikramaditya_and_rudrasimha_iii` (age=?, skin=medium-brown)

### Firuz Shah Tughlaq  
`canonical: firuz_shah_tughlaq`  

- **Canonical sheet:** `assets/_characters/firuz_shah_tughlaq/sheet.png`
- **Canonical look:** age=`?`, skin=`wheatish`
- **Appears in 2 entries:**
    - `bhanu_deva_iii_and_firuz_shah_tughlaq` (age=?, skin=medium-brown)  · skin wheatish→medium-brown

### Narasimhavarman I Mamalla  
`canonical: narasimhavarman_i_mamalla`  

- **Canonical sheet:** `assets/_characters/narasimhavarman_i_mamalla/sheet.png`
- **Canonical look:** age=`mid-30s`, skin=`medium-brown`
- **Appears in 2 entries:**
    - `pallavas_and_chalukyas` (age=?, skin=medium-brown)

### Banda Singh Bahadur  
`canonical: banda_singh_bahadur`  

- **Canonical sheet:** `assets/_characters/banda_singh_bahadur/sheet.png`
- **Canonical look:** age=`?`, skin=`wheatish`
- **Appears in 2 entries:**
    - `banda_singh_bahadur_and_wazir_khan` (age=mid-30s, skin=black)  ⚠️ SKIN wheatish→black

### Maharaja Ranjit Singh  
`canonical: maharaja_ranjit_singh`  

- **Canonical sheet:** `assets/_characters/maharaja_ranjit_singh/sheet.png`
- **Canonical look:** age=`?`, skin=`medium-brown`
- **Appears in 2 entries:**
    - `ranjit_singh_allard_and_ventura` (age=?, skin=dark)  · skin medium-brown→dark

### Krishnaraja Wodeyar III  
`canonical: krishnaraja_wodeyar_iii`  

- **Canonical sheet:** `assets/_characters/krishnaraja_wodeyar_iii/sheet.png`
- **Canonical look:** age=`?`, skin=`light-brown`
- **Appears in 2 entries:**
    - `krishnaraja_wodeyar_iii_and_chamaraja_wodeyar_x` (age=?, skin=?)

### Jassa Singh Ahluwalia  
`canonical: jassa_singh_ahluwalia`  

- **Canonical sheet:** `assets/_characters/jassa_singh_ahluwalia/sheet.png`
- **Canonical look:** age=`mid-40s`, skin=`wheatish`
- **Appears in 2 entries:**
    - `jassa_singh_ahluwalia_and_the_dal_khalsa` (age=?, skin=wheatish)

### Anangabhima Deva III  
`canonical: anangabhima_deva_iii`  

- **Canonical sheet:** `assets/_characters/anangabhima_deva_iii/sheet.png`
- **Canonical look:** age=`?`, skin=`medium-brown`
- **Appears in 2 entries:**
    - `anangabhima_deva_iii_and_general_vishnu` (age=?, skin=medium-brown)

### Eustachius De Lannoy  
`canonical: eustachius_de_lannoy`  

- **Canonical sheet:** `assets/_characters/eustachius_de_lannoy/sheet.png`
- **Canonical look:** age=`mid-40s`, skin=`brown`
- **Appears in 2 entries:**
    - `marthanda_varma_and_eustachius_de_lannoy` (age=?, skin=medium-brown)

### Mahmud Khalji I of Malwa  
`canonical: mahmud_khalji_i`  

- **Canonical sheet:** `assets/_characters/mahmud_khalji_i/sheet.png`
- **Canonical look:** age=`?`, skin=`medium-brown`
- **Appears in 2 entries:**
    - `mahmud_khalji_i_and_rana_kumbha` (age=?, skin=dark)  · skin medium-brown→dark

### Karikala Chola  
`canonical: karikala_chola`  

- **Canonical sheet:** `assets/_characters/karikala_chola/sheet.png`
- **Canonical look:** age=`mid-30s`, skin=`medium-brown`
- **Appears in 2 entries:**
    - `the_chera_chola_and_pandya_houses` (age=mid-30s, skin=medium-brown)

### Kumaragupta the First  
`canonical: kumaragupta_i`  

- **Canonical sheet:** `assets/_characters/kumaragupta_i/sheet.png`
- **Canonical look:** age=`?`, skin=`medium-brown`
- **Appears in 2 entries:**
    - `nalanda_seal_makers_and_kumaragupta_i` (age=mid-30s, skin=wheatish)  · skin medium-brown→wheatish

### Dara Shukoh  
`canonical: dara_shukoh`  

- **Canonical sheet:** `assets/_characters/dara_shukoh/sheet.png`
- **Canonical look:** age=`?`, skin=`pale`
- **Appears in 2 entries:**
    - `dara_shukoh_and_aurangzeb` (age=mid-30s, skin=pale)

### Govinda III Rashtrakuta  
`canonical: govinda_iii`  

- **Canonical sheet:** `assets/_characters/govinda_iii/sheet.png`
- **Canonical look:** age=`early-30s`, skin=`medium-brown`
- **Appears in 2 entries:**
    - `nagabhata_ii_dharmapala_and_govinda_iii` (age=?, skin=dusky)

### Malik Kafur  
`canonical: malik_kafur`  

- **Canonical sheet:** `assets/_characters/malik_kafur/sheet.png`
- **Canonical look:** age=`early-30s`, skin=`brown`
- **Appears in 2 entries:**
    - `ramachandra_deva_and_malik_kafur` (age=late-40s, skin=pale)  ⚠️ SKIN brown→pale

### Amir Khusrau  
`canonical: amir_khusrau`  

- **Canonical sheet:** `assets/_characters/amir_khusrau/sheet.png`
- **Canonical look:** age=`mid-40s`, skin=`medium-brown`
- **Appears in 2 entries:**
    - `amir_khusrau_and_vira_pandya` (age=?, skin=wheatish)  · skin medium-brown→wheatish

### Mahendravarman I  
`canonical: mahendravarman_i`  

- **Canonical sheet:** `assets/_characters/mahendravarman_i/sheet.png`
- **Canonical look:** age=`mid-30s`, skin=`medium-brown`
- **Appears in 2 entries:**
    - `appar_and_mahendravarman_i` (age=?, skin=?)

### Gautamiputra Śātakarṇi  
`canonical: gautamiputra_satakarni`  

- **Canonical sheet:** `assets/_characters/gautamiputra_satakarni/sheet.png`
- **Canonical look:** age=`?`, skin=`medium-brown`
- **Appears in 2 entries:**
    - `nahapana_and_gautamiputra_satakarni` (age=?, skin=tan)  · skin medium-brown→tan

### Bhaskara II (Bhaskaracharya)  
`canonical: bhaskara_ii`  

- **Canonical sheet:** `assets/_characters/bhaskara_ii/sheet.png`
- **Canonical look:** age=`40s`, skin=`brown`
- **Appears in 2 entries:**
    - `changadeva_and_bhaskara_ii` (age=late-30s, skin=medium-brown)

### Al-Biruni  
`canonical: al_biruni`  

- **Canonical sheet:** `assets/_characters/al_biruni/sheet.png`
- **Canonical look:** age=`late-40s`, skin=`brown`
- **Appears in 2 entries:**
    - `al_biruni_and_chand_bardai` (age=late-40s, skin=brown)

### Tipu Sultan  
`canonical: tipu_sultan`  

- **Canonical sheet:** `assets/_characters/tipu_sultan/sheet.png`
- **Canonical look:** age=`mid-30s`, skin=`medium-brown`
- **Appears in 2 entries:**
    - `tipu_sultan_and_george_harris` (age=?, skin=dark)  · skin medium-brown→dark

### Prataparudra II  
`canonical: prataparudra_ii`  

- **Canonical sheet:** `assets/_characters/prataparudra_ii/sheet.png`
- **Canonical look:** age=`mid-30s`, skin=`medium-brown`
- **Appears in 2 entries:**
    - `prataparudra_ii_and_ulugh_khan` (age=?, skin=medium-brown)

### Ibn Battuta in Calicut  
`canonical: ibn_battuta`  

- **Canonical sheet:** `assets/_characters/ibn_battuta/sheet.png`
- **Canonical look:** age=`mid-30s`, skin=`olive`
- **Appears in 2 entries:**
    - `ibn_battuta_and_t_s_burt` (age=?, skin=brown)  · skin olive→brown

### Azimullah Khan  
`canonical: azimullah_khan`  

- **Canonical sheet:** `assets/_characters/azimullah_khan/sheet.png`
- **Canonical look:** age=`?`, skin=`medium-brown`
- **Appears in 2 entries:**
    - `nana_sahib_and_azimullah_khan` (age=?, skin=wheatish)  · skin medium-brown→wheatish

### Rammohun Roy  
`canonical: rammohun_roy`  

- **Canonical sheet:** `assets/_characters/rammohun_roy/sheet.png`
- **Canonical look:** age=`?`, skin=`wheatish`
- **Appears in 2 entries:**
    - `rammohun_roy_and_lord_william_bentinck` (age=?, skin=light-brown)

### Rani Velu Nachiyar  
`canonical: velu_nachiyar`  

- **Canonical sheet:** `assets/_characters/velu_nachiyar/sheet.png`
- **Canonical look:** age=`late-20s`, skin=`brown`
- **Appears in 2 entries:**
    - `velu_nachiyar_and_kuyili` (age=?, skin=brown)

### Maharana Kumbha  
`canonical: maharana_kumbha`  

- **Canonical sheet:** `assets/_characters/maharana_kumbha/sheet.png`
- **Canonical look:** age=`?`, skin=`brown`
- **Appears in 2 entries:**
    - `sutradhar_jaita_and_maharana_kumbha` (age=?, skin=brown)

### Maharana Pratap  
`canonical: maharana_pratap`  

- **Canonical sheet:** `assets/_characters/maharana_pratap/sheet.png`
- **Canonical look:** age=`?`, skin=`brown`
- **Appears in 2 entries:**
    - `maharana_pratap_and_man_singh_i` (age=?, skin=wheatish)  · skin brown→wheatish

### Jayasimha Siddharaja  
`canonical: jayasimha_siddharaja`  

- **Canonical sheet:** `assets/_characters/jayasimha_siddharaja/sheet.png`
- **Canonical look:** age=`?`, skin=`wheatish`
- **Appears in 2 entries:**
    - `jayasimha_siddharaja_and_the_od_builders` (age=?, skin=wheatish)

### Sangram Shah (Aman Das)  
`canonical: sangram_shah`  

- **Canonical sheet:** `assets/_characters/sangram_shah/sheet.png`
- **Canonical look:** age=`mid-40s`, skin=`medium-brown`
- **Appears in 2 entries:**
    - `sangram_shah_and_bhanudatta_misra` (age=?, skin=deep-brown)  · skin medium-brown→deep-brown

### Bhillama V of Devagiri  
`canonical: bhillama_v`  

- **Canonical sheet:** `assets/_characters/bhillama_v/sheet.png`
- **Canonical look:** age=`mid-30s`, skin=`brown`
- **Appears in 2 entries:**
    - `bhillama_v_and_ballala_ii` (age=?, skin=wheatish)  · skin brown→wheatish

### Raghunatha Nayaka of Thanjavur  
`canonical: raghunatha_nayaka`  

- **Canonical sheet:** `assets/_characters/raghunatha_nayaka/sheet.png`
- **Canonical look:** age=`late-30s`, skin=`medium-brown`
- **Appears in 2 entries:**
    - `raghunatha_nayaka_and_ove_gjedde` (age=?, skin=medium-brown)

### Jamyang Namgyal  
`canonical: jamyang_namgyal`  

- **Canonical sheet:** `assets/_characters/jamyang_namgyal/sheet.png`
- **Canonical look:** age=`?`, skin=`tan`
- **Appears in 2 entries:**
    - `gyal_khatun_and_jamyang_namgyal` (age=early-thirties, skin=black)  ⚠️ SKIN tan→black

### Prataparudra Deva  
`canonical: prataparudra_deva`  

- **Canonical sheet:** `assets/_characters/prataparudra_deva/sheet.png`
- **Canonical look:** age=`early-40s`, skin=`deep-brown`
- **Appears in 2 entries:**
    - `prataparudra_deva_and_chaitanya` (age=early-40s, skin=medium-brown)  · skin deep-brown→medium-brown

### Demetrius I Aniketos  
`canonical: demetrius_i`  

- **Canonical sheet:** `assets/_characters/demetrius_i/sheet.png`
- **Canonical look:** age=`mid-30s`, skin=`olive`
- **Appears in 2 entries:**
    - `demetrius_i_and_the_builders_of_sirkap` (age=?, skin=olive)

### Pushyamitra Shunga  
`canonical: pushyamitra_shunga`  

- **Canonical sheet:** `assets/_characters/pushyamitra_shunga/sheet.png`
- **Canonical look:** age=`early-50s`, skin=`medium-brown`
- **Appears in 2 entries:**
    - `brihadratha_maurya_and_pushyamitra_shunga` (age=?, skin=brown)

### Rudradaman I  
`canonical: rudradaman_i`  

- **Canonical sheet:** `assets/_characters/rudradaman_i/sheet.png`
- **Canonical look:** age=`mid-30s`, skin=`wheatish-brown`
- **Appears in 2 entries:**
    - `rudradaman_i_and_vashishtiputra_satakarni` (age=?, skin=dark)  · skin wheatish-brown→dark

### Tailapa II of the Western Chalukyas  
`canonical: tailapa_ii`  

- **Canonical sheet:** `assets/_characters/tailapa_ii/sheet.png`
- **Canonical look:** age=`?`, skin=`medium-brown`
- **Appears in 2 entries:**
    - `tailapa_ii_and_karka_ii` (age=?, skin=black)  ⚠️ SKIN medium-brown→black

### Someshvara I Ahavamalla  
`canonical: someshvara_i`  

- **Canonical sheet:** `assets/_characters/someshvara_i/sheet.png`
- **Canonical look:** age=`late-30s`, skin=`medium-brown`
- **Appears in 2 entries:**
    - `someshvara_i_and_rajadhiraja_chola` (age=?, skin=brown)

### Sikandar Shah (Sikandar But-Shikan)  
`canonical: sikandar_shah`  

- **Canonical sheet:** `assets/_characters/sikandar_shah/sheet.png`
- **Canonical look:** age=`?`, skin=`black`
- **Appears in 2 entries:**
    - `sikandar_shah_and_firuz_shah_tughluq` (age=early-30s, skin=medium-brown)  ⚠️ SKIN black→medium-brown

### Ashoka Maurya  
`canonical: ashoka`  

- **Canonical sheet:** `assets/_characters/ashoka/sheet.png`
- **Canonical look:** age=`late-30s`, skin=`medium-brown`
- **Appears in 2 entries:**
    - `ashoka_and_dasharatha_maurya` (age=?, skin=bronze)

### Aśvaghoṣa  
`canonical: ashvaghosha`  

- **Canonical sheet:** `assets/_characters/ashvaghosha/sheet.png`
- **Canonical look:** age=`40s`, skin=`brown`
- **Appears in 2 entries:**
    - `vasumitra_and_ashvaghosha` (age=?, skin=dark)  · skin brown→dark

### Dharmapala of the Pala Dynasty  
`canonical: dharmapala`  

- **Canonical sheet:** `assets/_characters/dharmapala/sheet.png`
- **Canonical look:** age=`40s`, skin=`brown`
- **Appears in 2 entries:**
    - `dharmapala_and_atisha` (age=?, skin=medium-brown)

### Durlabhavardhana of Kashmir  
`canonical: durlabhavardhana`  

- **Canonical sheet:** `assets/_characters/durlabhavardhana/sheet.png`
- **Canonical look:** age=`late-30s`, skin=`dark`
- **Appears in 2 entries:**
    - `durlabhavardhana_and_lalitaditya` (age=?, skin=wheatish)  ⚠️ SKIN dark→wheatish

### Yashovarman of Jejakabhukti  
`canonical: yashovarman`  

- **Canonical sheet:** `assets/_characters/yashovarman/sheet.png`
- **Canonical look:** age=`early-30s`, skin=`medium-brown`
- **Appears in 2 entries:**
    - `yashovarman_of_kannauj_and_lalitaditya_of_kashmi` (age=?, skin=medium-brown)

### Hemachandra  
`canonical: hemachandra`  

- **Canonical sheet:** `assets/_characters/hemachandra/sheet.png`
- **Canonical look:** age=`40s`, skin=`brown`
- **Appears in 2 entries:**
    - `kumarapala_and_hemachandra` (age=?, skin=brown)

### Bāṇabhaṭṭa  
`canonical: banabhatta`  

- **Canonical sheet:** `assets/_characters/banabhatta/sheet.png`
- **Canonical look:** age=`?`, skin=`brown`
- **Appears in 2 entries:**
    - `banabhatta_and_bhushanabhatta` (age=?, skin=brown)

### Xuanzang  
`canonical: xuanzang`  

- **Canonical sheet:** `assets/_characters/xuanzang/sheet.png`
- **Canonical look:** age=`early-30s`, skin=`olive`
- **Appears in 2 entries:**
    - `silabhadra_and_xuanzang` (age=?, skin=brown)  · skin olive→brown

### Chashtana  
`canonical: chashtana`  

- **Canonical sheet:** `assets/_characters/chashtana/sheet.png`
- **Canonical look:** age=`mid-40s`, skin=`black`
- **Appears in 2 entries:**
    - `bhumaka_nahapana_and_chashtana` (age=mid-40s, skin=tan)  ⚠️ SKIN black→tan

### Rājaśekhara  
`canonical: rajashekhara`  

- **Canonical sheet:** `assets/_characters/rajashekhara/sheet.png`
- **Canonical look:** age=`mid-40s`, skin=`medium-brown`
- **Appears in 2 entries:**
    - `rajashekhara_and_avantisundari` (age=?, skin=medium-brown)

### Sthiramati  
`canonical: sthiramati`  

- **Canonical sheet:** `assets/_characters/sthiramati/sheet.png`
- **Canonical look:** age=`mid-30s`, skin=`brown`
- **Appears in 2 entries:**
    - `gunamati_and_sthiramati` (age=?, skin=wheatish)  · skin brown→wheatish

## Methodology

- Source of truth: `characters/registry.json` (each entry = one character sheet used by the art pipeline).
- A **recurring person** = a standalone slug whose name-tokens appear as a contiguous run inside one or more composite `X_and_Y` slugs.
- Skin tone is read from the introducing clause of each `ref_desc` and mapped to a 5-step fair→black scale; age from `early/mid/late-N0s` phrasing.
- Only ≥2 tone steps or ≈20+ apparent years raise a ⚠️; smaller gaps are noted with ·. Automated heuristic — treat as a review worklist, not gospel.

## Recommendation (for when Azure generation resumes)

1. For each ⚠️ person, pick the **canonical sheet** as the reference and re-issue the drifted per-story sheets with the canonical `ref_desc` (same age band + skin tone + signature attire).
2. Prefer **reusing** the canonical sheet in group scenes over regenerating a fresh look per story.
3. Re-run this audit (`files/char_bible.py`) after fixes to confirm the ⚠️ count drops.

