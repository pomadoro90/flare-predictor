using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEngine;
using UnityEngine.UI;
using TMPro;

/// <summary>
/// Режим «Архив»: загрузка CSV-файла (100 записей), перебор замеров,
/// обновление индикаторов датчиков и проверка нарушений.
/// </summary>
public class ArchiveMode : MonoBehaviour
{
    [Header("UI элементы")]
    public Slider recordSlider;
    public TMP_Text recordNumberText;
    public TMP_Text alertText;
    public TMP_Text valuesText;
    public GameObject alertPanel;

    [Header("Индикаторы датчиков")]
    public MeshRenderer sensorPFlare;    // датчик P_flare на сепараторе
    public MeshRenderer sensorPFlareIndicator;
    public MeshRenderer sensorPPurge;    // датчик P_purge на факеле
    public MeshRenderer sensorQPurge;    // датчик Q_purge
    public MeshRenderer sensorTFlame;    // датчик T_flame
    public MeshRenderer sensorSteam;
    public MeshRenderer otrivIndicator;  // лампа отрыва
    public MeshRenderer hlopokIndicator; // лампа хлопка

    [Header("Эффект пламени")]
    public ParticleSystem flareParticles;
    public Light flareLight;
    public Color normalFlameColor = new Color(1f, 0.6f, 0.1f);
    public Color warningFlameColor = new Color(1f, 0.85f, 0.1f);
    public Color dangerFlameColor = new Color(1f, 0.15f, 0.05f);

    private List<FlareRecord> records = new List<FlareRecord>();
    private int currentIndex = 0;

    // Границы норм
    private const float P_FLARE_MIN = 0.004f;
    private const float P_FLARE_MAX = 0.016f;
    private const float Q_FLARE_MIN = 1.5f;
    private const float P_PURGE_MIN = 0.3f;
    private const float P_PURGE_MAX = 0.6f;
    private const float Q_PURGE_MIN = 20f;
    private const float Q_PURGE_MAX = 50f;
    private const float T_FLAME_MIN = 800f;
    private const float T_FLAME_MAX = 1200f;

    // Границы аварий
    private const float P_PURGE_CRITICAL = 0.28f;
    private const float Q_PURGE_CRITICAL = 22f;
    private const float P_FLARE_CRITICAL = 0.022f;

    void Start()
    {
        LoadCSV();
        recordSlider.minValue = 0;
        recordSlider.maxValue = records.Count - 1;
        recordSlider.wholeNumbers = true;
        recordSlider.onValueChanged.AddListener(OnSliderChanged);
        ShowRecord(0);
    }

    void LoadCSV()
    {
        string path = Path.Combine(Application.streamingAssetsPath, "variant_3_4.csv");
        string[] lines = File.ReadAllLines(path);
        for (int i = 1; i < lines.Length; i++) // первая строка — заголовок
        {
            string[] cols = lines[i].Split(';');
            if (cols.Length < 9) continue;

            records.Add(new FlareRecord
            {
                N        = int.Parse(cols[0]),
                P_flare  = float.Parse(cols[1]),
                Q_flare  = float.Parse(cols[2]),
                P_purge  = float.Parse(cols[3]),
                Q_purge  = float.Parse(cols[4]),
                T_flame  = float.Parse(cols[5]),
                Steam_Q  = float.Parse(cols[6]),
                otriv    = int.Parse(cols[7]),
                hlopok   = int.Parse(cols[8])
            });
        }
        Debug.Log($"Загружено {records.Count} записей");
    }

    void OnSliderChanged(float value)
    {
        currentIndex = (int)value;
        ShowRecord(currentIndex);
    }

    void ShowRecord(int index)
    {
        if (index < 0 || index >= records.Count) return;
        FlareRecord r = records[index];

        recordNumberText.text = $"Замер №{r.N} / {records.Count}";
        valuesText.text = $"P_flare: {r.P_flare:F3} МПа | Q_flare: {r.Q_flare:F1} м³/ч\n" +
                         $"P_purge: {r.P_purge:F2} МПа | Q_purge: {r.Q_purge:F0} м³/ч\n" +
                         $"T_flame: {r.T_flame:F0} °C | Steam: {r.Steam_Q:F0} кг/ч";

        // Обновление цвета датчиков
        UpdateSensorColor(sensorPFlare, r.P_flare, P_FLARE_MIN, P_FLARE_MAX);
        UpdateSensorColor(sensorPPurge, r.P_purge, P_PURGE_MIN, P_PURGE_MAX);
        UpdateSensorColor(sensorQPurge, r.Q_purge, Q_PURGE_MIN, Q_PURGE_MAX);
        UpdateSensorColor(sensorTFlame, r.T_flame, T_FLAME_MIN, T_FLAME_MAX);

        // Индикаторы аварий
        Color red = new Color(0.9f, 0.1f, 0.1f);
        Color green = new Color(0.1f, 0.8f, 0.2f);
        Color off = new Color(0.2f, 0.2f, 0.2f);

        otrivIndicator.material.color = r.otriv == 1 ? red : off;
        hlopokIndicator.material.color = r.hlopok == 1 ? red : off;

        // Анализ нарушений
        string alertMsg = "";
        bool hasAlert = false;

        if (r.P_purge < P_PURGE_CRITICAL && r.Q_purge < Q_PURGE_CRITICAL)
        {
            alertMsg += "⚠️ РИСК ОТРЫВА ПЛАМЕНИ! Увеличить расход продувочного газа.\n";
            hasAlert = true;
        }
        if (r.P_flare > P_FLARE_CRITICAL)
        {
            alertMsg += "⚠️ Высокое давление сброса! Опасность хлопка.\n";
            hasAlert = true;
        }
        if (r.Q_flare < Q_FLARE_MIN)
        {
            alertMsg += "⚠️ Низкий расход сбросного газа. Проверить подачу.\n";
            hasAlert = true;
        }
        if (r.P_purge < P_PURGE_MIN || r.P_purge > P_PURGE_MAX)
        {
            alertMsg += $"⚠️ Давление продувочного газа вне нормы ({r.P_purge:F2} МПа).\n";
            hasAlert = true;
        }
        if (r.T_flame < T_FLAME_MIN || r.T_flame > T_FLAME_MAX)
        {
            alertMsg += $"⚠️ Температура факела вне нормы ({r.T_flame:F0} °C).\n";
            hasAlert = true;
        }

        alertPanel.SetActive(hasAlert);
        alertText.text = hasAlert ? alertMsg : "Все параметры в норме ✓";

        // Цвет пламени
        UpdateFlameColor(r);
    }

    void UpdateSensorColor(MeshRenderer sensor, float value, float min, float max)
    {
        if (value < min || value > max)
            sensor.material.color = new Color(0.9f, 0.1f, 0.1f); // красный — нарушение
        else
            sensor.material.color = new Color(0.1f, 0.8f, 0.2f); // зелёный — норма
    }

    void UpdateFlameColor(FlareRecord r)
    {
        Color targetColor;
        float intensity;

        if (r.otriv == 1 || r.hlopok == 1)
        {
            targetColor = dangerFlameColor;
            intensity = 0.3f;
        }
        else if (r.P_purge < P_PURGE_CRITICAL && r.Q_purge < Q_PURGE_CRITICAL)
        {
            targetColor = warningFlameColor;
            intensity = 1.2f;
        }
        else
        {
            targetColor = normalFlameColor;
            intensity = 2.0f;
        }

        var main = flareParticles.main;
        main.startColor = targetColor;
        flareLight.color = targetColor;
        flareLight.intensity = intensity;
    }

    public void NextRecord() { ShowRecord(Mathf.Min(currentIndex + 1, records.Count - 1)); recordSlider.value = currentIndex; }
    public void PrevRecord() { ShowRecord(Mathf.Max(currentIndex - 1, 0)); recordSlider.value = currentIndex; }
}

[System.Serializable]
public class FlareRecord
{
    public int N;
    public float P_flare, Q_flare, P_purge, Q_purge, T_flame, Steam_Q;
    public int otriv, hlopok;
}
