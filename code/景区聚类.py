import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import warnings
import os

# -------------------------- 1. 配置保存路径 --------------------------
# 结果保存目录
save_dir = 'D:/大数据/聚类结果/'
os.makedirs(save_dir, exist_ok=True)  # 确保目录存在，避免保存失败

# -------------------------- 2. 屏蔽警告 & 中文配置 --------------------------
warnings.filterwarnings('ignore', category=UserWarning)
plt.rcParams["font.family"] = ["SimHei"]
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 300  # 提高图片分辨率，保存更清晰

# -------------------------- 3. 加载数据 & 预处理 --------------------------
df = pd.read_csv('D:/大数据/情感分析结果（限制情感大类）.csv')

# 计算情感得分
df['sentiment_num'] = df['sentiment'].map({'正面': 1, '负面': -1, '中性': 0})
df['sentiment_score'] = df['sentiment_num'] * df['intensity']

# 按景区聚合（一景一类）
scenic_agg = df.groupby('name').agg(
    avg_sentiment_score=('sentiment_score', 'mean'),
    main_type=('tag2', lambda x: x.mode()[0]),
    avg_lon=('lon', 'mean'),
    avg_lat=('lat', 'mean'),
    record_count=('name', 'count')
).reset_index()

# -------------------------- 4. 聚类特征准备 --------------------------
X = scenic_agg[['main_type', 'avg_sentiment_score', 'avg_lon', 'avg_lat']]
X = pd.get_dummies(X, columns=['main_type'])
X = X.dropna()

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# -------------------------- 5. 选择最优簇数 & 保存轮廓系数图 --------------------------
silhouette_scores = []
cluster_range = range(2, 11)
for k in cluster_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(X_scaled)
    silhouette_scores.append(silhouette_score(X_scaled, kmeans.labels_))

# 绘制并保存轮廓系数图
plt.figure(figsize=(8, 5))
plt.plot(cluster_range, silhouette_scores, marker='o', color='#FF6B6B', linewidth=2)
plt.xlabel('簇数（K）', fontsize=12)
plt.ylabel('轮廓系数', fontsize=12)
plt.title('轮廓系数法选择最优簇数', fontsize=14, pad=20)
plt.grid(alpha=0.3, linestyle='--')
plt.xticks(cluster_range)
# 保存图片（PNG格式，清晰无压缩）
plt.savefig(f'{save_dir}轮廓系数图.png', bbox_inches='tight')  # bbox_inches确保标签完整
plt.close()  # 关闭图片，释放内存

# 确定最优簇数
best_k = cluster_range[silhouette_scores.index(max(silhouette_scores))]
print(f'【最优聚类数量】: {best_k}，结果已保存至 {save_dir}\n')

# -------------------------- 6. 执行聚类 --------------------------
kmeans = KMeans(n_clusters=best_k, random_state=42, n_init=10)
scenic_agg['cluster_label'] = kmeans.fit_predict(X_scaled)

# -------------------------- 7. 聚类结果可视化 & 保存散点图 --------------------------
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)
scenic_agg['pca_x'] = X_pca[:, 0]
scenic_agg['pca_y'] = X_pca[:, 1]

# 绘制并保存散点图
plt.figure(figsize=(10, 8))
colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9FF3']
for cluster in range(best_k):
    cluster_data = scenic_agg[scenic_agg['cluster_label'] == cluster]
    plt.scatter(
        cluster_data['pca_x'],
        cluster_data['pca_y'],
        c=colors[cluster % len(colors)],
        label=f'聚类{cluster + 1}（{len(cluster_data)}个景区）',
        alpha=0.8,
        s=80
    )
plt.xlabel(f'主成分1（解释方差：{pca.explained_variance_ratio_[0]:.1%}）', fontsize=11)
plt.ylabel(f'主成分2（解释方差：{pca.explained_variance_ratio_[1]:.1%}）', fontsize=11)
plt.title('景区聚类结果（按类型、情感、经纬度）', fontsize=14, pad=20)
plt.legend(loc='best', fontsize=10)
plt.grid(alpha=0.3, linestyle='--')
# 保存散点图
plt.savefig(f'{save_dir}聚类结果散点图.png', bbox_inches='tight')
plt.close()

# -------------------------- 8. 保存聚类结果为CSV --------------------------
# 整理CSV结果（包含所有关键信息）
result_df = scenic_agg[['name', 'cluster_label', 'avg_sentiment_score',
                        'main_type', 'avg_lon', 'avg_lat', 'record_count']]
# 重命名列名，便于阅读
result_df.columns = ['景区名称', '聚类标签', '平均情感得分', '主要类型', '平均经度', '平均纬度', '评价记录数']
# 保存为CSV（utf-8编码，兼容Excel）
result_df.to_csv(f'{save_dir}景区聚类结果.csv', index=False, encoding='utf-8-sig')

# -------------------------- 9. 控制台输出简要结果 --------------------------
print('=' * 100)
print(f'【结果保存完成】\n'
      f'1. 聚类详细数据：{save_dir}景区聚类结果.csv\n'
      f'2. 轮廓系数图：{save_dir}轮廓系数图.png\n'
      f'3. 聚类散点图：{save_dir}聚类结果散点图.png')
print('=' * 100)