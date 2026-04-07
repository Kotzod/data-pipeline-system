import luigi
import pandas as pd
import os


class ValidateTask(luigi.Task):
    def output(self):
        return luigi.LocalTarget('output/validated_data.csv')

    def run(self):
        os.makedirs('output', exist_ok=True)

        # Load both CSV files
        df1 = pd.read_csv('data1.csv')
        df2 = pd.read_csv('data2.csv')

        # Fix missing humidity values in data2 with the mean
        df2['humidity_rel_perc'] = df2['humidity_rel_perc'].fillna(df2['humidity_rel_perc'].mean())

        # Merge on location and time
        df = pd.merge(df1, df2, on=['location', 'time'])
        df.to_csv(self.output().path, index=False)
        print(f"Step 1 done: {len(df)} records validated and merged")


# STEP 2: Analyze and add calculated fields
class AnalyzeTask(luigi.Task):
    def requires(self):
        return ValidateTask()  # depends on Step 1

    def output(self):
        return luigi.LocalTarget('output/analyzed_data.csv')

    def run(self):
        df = pd.read_csv(self.input().path)

        # Added comfort index
        df['comfort_index'] = 100 - abs(df['temperature_C'] - 22) * 2 - abs(df['humidity_rel_perc'] - 45) * 0.5

        # Flag high CO2 (above 450 ppm)
        df['high_co2'] = df['CO2_ppm'] > 450

        # Anomaly detection using z-scores (flag if |z| > 2)
        for col in ['CO2_ppm', 'temperature_C', 'humidity_rel_perc']:
            mean, std = df[col].mean(), df[col].std()
            df[f'{col}_zscore'] = (df[col] - mean) / std

        # Flag as anomaly if ANY measurement has z-score > 2
        df['is_anomaly'] = (
            (df['CO2_ppm_zscore'].abs() > 2) |
            (df['temperature_C_zscore'].abs() > 2) |
            (df['humidity_rel_perc_zscore'].abs() > 2)
        )

        df.to_csv(self.output().path, index=False)
        print(f"Step 2 done: {df['high_co2'].sum()} CO2 warnings, {df['is_anomaly'].sum()} anomalies")


# STEP 3: Generate report
class ReportTask(luigi.Task):
    def requires(self):
        return AnalyzeTask()

    def output(self):
        return luigi.LocalTarget('output/report.txt')

    def run(self):
        df = pd.read_csv(self.input().path)

        # Build simple report
        lines = ["=== ENVIRONMENTAL REPORT ===\n"]
        lines.append(f"Total records: {len(df)}\n")

        # Stats per location
        for loc in df['location'].unique():
            loc_data = df[df['location'] == loc]
            lines.append(f"\nLocation {loc}:")
            lines.append(f"  Avg CO2: {loc_data['CO2_ppm'].mean():.1f} ppm")
            lines.append(f"  Avg Temp: {loc_data['temperature_C'].mean():.1f} C")
            lines.append(f"  High CO2 warnings: {loc_data['high_co2'].sum()}")

        # List anomalies
        anomalies = df[df['is_anomaly']]
        lines.append(f"\n\n=== ANOMALIES DETECTED: {len(anomalies)} ===")
        if len(anomalies) > 0:
            for _, row in anomalies.iterrows():
                lines.append(f"  Location {row['location']}, Time {row['time']}")
        else:
            lines.append("  None - all readings normal")

        with open(self.output().path, 'w') as f:
            f.write('\n'.join(lines))

        print(f"Step 3 done: report saved to {self.output().path}")


if __name__ == '__main__':
    luigi.build([ReportTask()], local_scheduler=False)
