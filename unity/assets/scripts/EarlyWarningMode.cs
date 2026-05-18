using UnityEngine;
using UnityEngine.UI;
using TMPro;
using System;

/// <summary>
/// Режим «Раннее предупреждение»: прогнозирование вероятности отрыва пламени
/// на основе логистической регрессии с ползунками параметров.
/// Коэффициенты получены на этапе статистической обработки (stats/):
/// b0=6.679249, b1=-13.278002, b2=-0.185235, b3=-0.010987
/// </summary>
public class EarlyWarningMode : MonoBehaviour
{
    [Header("Ползунки параметров")]
    public Slider ppurgeSlider;
    public Slider qpurgeSlider;
    public Slider pflareSlider;

    [Header("Отображение значений")]
    public TMP_Text ppurgeValueText;
    public TMP_Text qpurgeValueText;
    public TMP_Text pflareValueText;
    public TMP_Text probabilityText;
    public TMP_Text recommendationText;

    [Header("Шкала риска")]
    public Image riskBarFill;
    public Image riskBarBackground;
    public Gradient riskGradient;

    [Header("Эффект пламени")]
    public ParticleSystem flareParticles;
    public Light flareLight;

    [Header("Аварийная сигнализация")]
    public GameObject alarmPanel;
    public AudioSource alarmSound;
    public Light alarmLight;

    // Коэффициенты логистической регрессии
    private const float B0 = 6.679249f;
    private const float B1 = -13.278002f;
    private const float B2 = -0.185235f;
    private const float B3 = -0.010987f;

    // Пороги вероятности
    private const float GREEN_THRESHOLD = 0.3f;   // P < 0.3 — зелёный
    private const float YELLOW_THRESHOLD = 0.7f;  // 0.3 ≤ P < 0.7 — жёлтый
                                                    // P ≥ 0.7 — красный

    private float currentProbability = 0f;

    void Start()
    {
        // Настройка ползунков
        ppurgeSlider.minValue = 0.1f;
        ppurgeSlider.maxValue = 0.6f;
        ppurgeSlider.value = 0.35f;
        ppurgeSlider.onValueChanged.AddListener(OnParamChanged);

        qpurgeSlider.minValue = 5f;
        qpurgeSlider.maxValue = 50f;
        qpurgeSlider.value = 25f;
        qpurgeSlider.onValueChanged.AddListener(OnParamChanged);

        pflareSlider.minValue = 0.004f;
        pflareSlider.maxValue = 0.030f;
        pflareSlider.value = 0.012f;
        pflareSlider.onValueChanged.AddListener(OnParamChanged);

        // Инициализация
        OnParamChanged(0f);
        alarmPanel.SetActive(false);
    }

    void OnParamChanged(float _)
    {
        float P_purge = ppurgeSlider.value;
        float Q_purge = qpurgeSlider.value;
        float P_flare = pflareSlider.value;

        ppurgeValueText.text = $"{P_purge:F3} МПа";
        qpurgeValueText.text = $"{Q_purge:F0} м³/ч";
        pflareValueText.text = $"{P_flare:F3} МПа";

        // Расчёт вероятности отрыва
        currentProbability = PredictProbability(P_purge, Q_purge, P_flare);
        probabilityText.text = $"{(currentProbability * 100f):F1}%";

        // Обновление шкалы риска
        UpdateRiskBar();

        // Обновление цвета пламени
        UpdateFlameColor();

        // Рекомендации
        UpdateRecommendations(P_purge, Q_purge, P_flare);

        // Аварийная сигнализация
        UpdateAlarm();
    }

    float PredictProbability(float P_purge, float Q_purge, float P_flare)
    {
        // Логит: z = b0 + b1·x1 + b2·x2 + b3·x3
        float z = B0 + B1 * P_purge + B2 * Q_purge + B3 * P_flare;
        // Сигмоида
        return 1f / (1f + Mathf.Exp(-z));
    }

    void UpdateRiskBar()
    {
        float fill = Mathf.Clamp01(currentProbability);
        riskBarFill.fillAmount = fill;
        riskBarFill.color = riskGradient.Evaluate(fill);

        // Цвет фона шкалы тоже меняется
        if (currentProbability < GREEN_THRESHOLD)
            riskBarBackground.color = new Color(0.1f, 0.6f, 0.2f, 0.3f);
        else if (currentProbability < YELLOW_THRESHOLD)
            riskBarBackground.color = new Color(1f, 0.7f, 0.1f, 0.3f);
        else
            riskBarBackground.color = new Color(0.9f, 0.1f, 0.1f, 0.3f);
    }

    void UpdateFlameColor()
    {
        Color flameColor;
        float intensity;

        if (currentProbability < GREEN_THRESHOLD)
        {
            // Стабильное зелёное пламя
            flameColor = new Color(0.1f, 0.9f, 0.2f);
            intensity = 2.5f;
        }
        else if (currentProbability < YELLOW_THRESHOLD)
        {
            // Нестабильное жёлтое пламя
            flameColor = new Color(1f, 0.85f, 0.1f);
            intensity = 1.5f;
        }
        else
        {
            // Затухающее красное пламя
            flameColor = new Color(1f, 0.15f, 0.05f);
            intensity = 0.5f;
        }

        var main = flareParticles.main;
        main.startColor = flameColor;
        flareLight.color = flameColor;
        flareLight.intensity = intensity;
    }

    void UpdateRecommendations(float P_purge, float Q_purge, float P_flare)
    {
        string rec = "";

        if (currentProbability > YELLOW_THRESHOLD)
        {
            rec = "🔴 КРИТИЧЕСКИЙ РИСК ОТРЫВА ПЛАМЕНИ!\n";

            if (P_purge < 0.28f)
                rec += "• Немедленно увеличьте давление продувочного газа\n";
            if (Q_purge < 22f)
                rec += "• Увеличьте расход продувочного газа\n";
            if (P_flare > 0.022f)
                rec += "• Снизьте давление сброса — риск хлопка\n";

            rec += "• Проверьте подачу инертного газа в коллектор\n";
        }
        else if (currentProbability > GREEN_THRESHOLD)
        {
            rec = "🟡 ПОВЫШЕННЫЙ РИСК — требуется внимание\n";

            if (P_purge < 0.35f)
                rec += "• Рекомендуется увеличить давление продувочного газа\n";
            if (Q_purge < 28f)
                rec += "• Рекомендуется увеличить расход продувочного газа\n";
        }
        else
        {
            rec = "🟢 Режим стабильный. Параметры в норме.";
        }

        recommendationText.text = rec;
    }

    void UpdateAlarm()
    {
        bool shouldAlarm = currentProbability > 0.8f;

        if (shouldAlarm && !alarmPanel.activeSelf)
        {
            alarmPanel.SetActive(true);
            if (alarmSound != null) alarmSound.Play();
        }
        else if (!shouldAlarm && alarmPanel.activeSelf)
        {
            alarmPanel.SetActive(false);
            if (alarmSound != null) alarmSound.Stop();
        }

        // Мигание аварийной лампы
        if (alarmLight != null)
        {
            alarmLight.enabled = shouldAlarm && (Time.time % 1f < 0.5f);
            alarmLight.color = Color.red;
        }
    }

    // Сброс к безопасным значениям
    public void ResetToSafe()
    {
        ppurgeSlider.value = 0.45f;
        qpurgeSlider.value = 35f;
        pflareSlider.value = 0.010f;
    }
}
