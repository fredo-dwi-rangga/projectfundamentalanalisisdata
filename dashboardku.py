import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import folium
from streamlit_folium import st_folium

# ============================================
# CONFIG
# ============================================
st.set_page_config(
    page_title="E-Commerce Dashboard",
    page_icon="🛒",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    /* Font & Background */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .main {
        background-color: #F8F9FC;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1f36 0%, #111827 100%);
    }
    section[data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
    section[data-testid="stSidebar"] .stRadio label {
        background: rgba(255,255,255,0.05);
        border-radius: 8px;
        padding: 8px 12px;
        margin: 2px 0;
        transition: background 0.2s;
    }
    section[data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(255,255,255,0.12);
    }

    /* Metric Cards */
    [data-testid="metric-container"] {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }

    /* Headers */
    h1 { color: #1a1f36; font-weight: 700; }
    h2, h3 { color: #2d3748; font-weight: 600; }

    /* Divider */
    hr { border-color: #e2e8f0; margin: 1.5rem 0; }

    /* Info/Warning/Error boxes */
    .stInfo, .stWarning, .stSuccess, .stError {
        border-radius: 10px;
    }

    /* Dataframe */
    [data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        color: #64748b;
    }
    .stTabs [aria-selected="true"] {
        color: #1a1f36;
        border-bottom-color: #1a1f36;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# LOAD DATA
# ============================================
@st.cache_data
def load_data():
    main_df               = pd.read_csv('data/main_data.csv')
    rfm_df                = pd.read_csv('data/rfm_data.csv')
    top_category_order    = pd.read_csv('data/top_category_order.csv')
    top_category_revenue  = pd.read_csv('data/top_category_revenue.csv')
    monthly_order         = pd.read_csv('data/monthly_order.csv')
    delivery_summary      = pd.read_csv('data/delivery_summary.csv')
    top_city              = pd.read_csv('data/top_city.csv')
    top_payment           = pd.read_csv('data/top_payment.csv')
    location_df           = pd.read_csv('data/geolocation_dataset.csv')
    main_df['order_purchase_timestamp'] = pd.to_datetime(main_df['order_purchase_timestamp'])
    return (main_df, rfm_df, top_category_order, top_category_revenue,
            monthly_order, delivery_summary, top_city, top_payment, location_df)

(main_df, rfm_df, top_category_order, top_category_revenue,
 monthly_order, delivery_summary, top_city, top_payment, location_df) = load_data()

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.markdown("## 🛒 E-Commerce")
    st.markdown("### Dashboard Analisis")
    st.markdown("---")

    page = st.radio("📌 Menu", [
        "🏠 Overview",
        "📦 Analisis Produk",
        "📈 Tren & Pengiriman",
        "🏙️ Analisis Pelanggan",
        "💳 Metode Pembayaran",
        "🗺️ Geospatial Analysis",
        "👥 Customer Segmentation",
        "📌 Conclusion"
    ])

    st.markdown("---")
    st.markdown("### 🗓️ Filter Tanggal")
    min_date = main_df['order_purchase_timestamp'].min().date()
    max_date = main_df['order_purchase_timestamp'].max().date()
    start_date = st.date_input("Dari", min_date)
    end_date   = st.date_input("Sampai", max_date)

    st.markdown("---")
    st.caption("© 2024 E-Commerce Dashboard")

# Filter data
filtered_df = main_df[
    (main_df['order_purchase_timestamp'].dt.date >= start_date) &
    (main_df['order_purchase_timestamp'].dt.date <= end_date)
]

# ============================================
# HELPER: PLOT STYLE
# ============================================
def set_style():
    plt.rcParams.update({
        'figure.facecolor': 'white',
        'axes.facecolor':   'white',
        'axes.spines.top':  False,
        'axes.spines.right':False,
        'axes.grid':        True,
        'grid.alpha':       0.3,
        'grid.linestyle':   '--',
        'font.family':      'sans-serif',
    })

# ============================================
# PAGE 1: OVERVIEW
# ============================================
if page == "🏠 Overview":
    st.title("🏠 Overview")
    st.markdown("Ringkasan keseluruhan performa e-commerce berdasarkan periode yang dipilih.")
    st.markdown("---")

    # Metric cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🛍️ Total Order",    f"{filtered_df['order_id'].nunique():,}")
    with col2:
        st.metric("👥 Total Customer", f"{filtered_df['customer_unique_id'].nunique():,}")
    with col3:
        st.metric("💰 Total Revenue",  f"R${filtered_df['price'].sum():,.0f}")
    with col4:
        st.metric("📦 Avg Order Value",f"R${filtered_df['price'].mean():,.0f}")

    st.markdown("---")

    # Tren bulanan
    st.subheader("📈 Tren Order Bulanan")
    filtered_df['year_month'] = filtered_df['order_purchase_timestamp'].dt.to_period('M').astype(str)
    monthly = filtered_df.groupby('year_month')['order_id'].count().reset_index()
    monthly.columns = ['year_month', 'total_order']

    set_style()
    fig, ax = plt.subplots(figsize=(14, 4))
    ax.plot(monthly['year_month'], monthly['total_order'],
            marker='o', color='#1a1f36', linewidth=2.5, markersize=5)
    ax.fill_between(monthly['year_month'], monthly['total_order'],
                    alpha=0.15, color='#1a1f36')
    ax.set_xlabel('Bulan', fontsize=11)
    ax.set_ylabel('Total Order', fontsize=11)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig)

    st.markdown("---")

    # Top 5 kategori & kota
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🏆 Top 5 Kategori")
        data = top_category_order.head(5)
        set_style()
        fig, ax = plt.subplots(figsize=(8, 4))
        bars = ax.barh(data['category'], data['total_order'],
                       color=['#1a1f36','#2d3a6b','#3d5a9e','#6b86c4','#a8b8e8'])
        ax.set_xlabel('Total Order')
        ax.invert_yaxis()
        for bar, val in zip(bars, data['total_order']):
            ax.text(bar.get_width() + 50, bar.get_y() + bar.get_height()/2,
                    f'{val:,}', va='center', fontsize=9)
        plt.tight_layout()
        st.pyplot(fig)

    with col2:
        st.subheader("🏙️ Top 5 Kota")
        data = top_city.head(5)
        set_style()
        fig, ax = plt.subplots(figsize=(8, 4))
        bars = ax.barh(data['city'], data['total_customer'],
                       color=['#1a4731','#1e6b47','#28a063','#5cc891','#a8e6c8'])
        ax.set_xlabel('Total Customer')
        ax.invert_yaxis()
        for bar, val in zip(bars, data['total_customer']):
            ax.text(bar.get_width() + 50, bar.get_y() + bar.get_height()/2,
                    f'{val:,}', va='center', fontsize=9)
        plt.tight_layout()
        st.pyplot(fig)

# ============================================
# PAGE 2: ANALISIS PRODUK
# ============================================
elif page == "📦 Analisis Produk":
    st.title("📦 Analisis Kategori Produk")
    st.markdown("Kategori produk apa yang paling banyak di-order dan menghasilkan revenue tertinggi?")
    st.markdown("---")

    top_n = st.slider("🔢 Tampilkan Top N Kategori", 5, 20, 10)
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 Terbanyak di-Order")
        data = top_category_order.head(top_n)
        set_style()
        fig, ax = plt.subplots(figsize=(10, 7))
        palette = sns.color_palette("Blues_r", top_n)
        bars = ax.barh(data['category'], data['total_order'], color=palette)
        ax.invert_yaxis()
        ax.set_xlabel('Total Order', fontsize=11)
        for bar, val in zip(bars, data['total_order']):
            ax.text(bar.get_width() + 30, bar.get_y() + bar.get_height()/2,
                    f'{val:,}', va='center', fontsize=9)
        plt.tight_layout()
        st.pyplot(fig)

    with col2:
        st.subheader("💰 Revenue Tertinggi")
        data = top_category_revenue.head(top_n)
        set_style()
        fig, ax = plt.subplots(figsize=(10, 7))
        palette = sns.color_palette("Greens_r", top_n)
        bars = ax.barh(data['category'], data['total_revenue'], color=palette)
        ax.invert_yaxis()
        ax.set_xlabel('Total Revenue (R$)', fontsize=11)
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'R${x/1e6:.1f}M'))
        for bar, val in zip(bars, data['total_revenue']):
            ax.text(bar.get_width() + 1000, bar.get_y() + bar.get_height()/2,
                    f'R${val:,.0f}', va='center', fontsize=8)
        plt.tight_layout()
        st.pyplot(fig)

    st.markdown("---")
    st.subheader("📋 Tabel Detail")
    tab1, tab2 = st.tabs(["By Order", "By Revenue"])
    with tab1:
        st.dataframe(top_category_order, use_container_width=True)
    with tab2:
        st.dataframe(top_category_revenue, use_container_width=True)

# ============================================
# PAGE 3: TREN & PENGIRIMAN
# ============================================
elif page == "📈 Tren & Pengiriman":
    st.title("📈 Tren Order & Ketepatan Pengiriman")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📅 Tren Order per Bulan")
        set_style()
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(monthly_order['year_month'], monthly_order['total_order'],
                marker='o', color='#1a1f36', linewidth=2.5, markersize=5)
        ax.fill_between(monthly_order['year_month'],
                        monthly_order['total_order'], alpha=0.15, color='#1a1f36')
        ax.set_xlabel('Bulan')
        ax.set_ylabel('Total Order')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig)

    with col2:
        st.subheader("🚚 Status Ketepatan Pengiriman")
        set_style()
        colors = ['#28a063', '#e53e3e']
        fig, ax = plt.subplots(figsize=(8, 5))
        wedges, texts, autotexts = ax.pie(
            delivery_summary['total'],
            labels=delivery_summary['status'],
            autopct='%1.1f%%',
            colors=colors,
            startangle=90,
            wedgeprops={'edgecolor': 'white', 'linewidth': 2.5}
        )
        for text in autotexts:
            text.set_fontsize(12)
            text.set_fontweight('bold')
        plt.tight_layout()
        st.pyplot(fig)

    st.markdown("---")
    st.subheader("📋 Detail Status Pengiriman")
    st.dataframe(delivery_summary, use_container_width=True)

# ============================================
# PAGE 4: ANALISIS PELANGGAN
# ============================================
elif page == "🏙️ Analisis Pelanggan":
    st.title("🏙️ Analisis Pelanggan per Kota")
    st.markdown("---")

    top_n_city = st.slider("🔢 Tampilkan Top N Kota", 5, 20, 10)

    set_style()
    fig, ax = plt.subplots(figsize=(10, 6))
    palette = sns.color_palette("Oranges_r", top_n_city)
    data = top_city.head(top_n_city)
    bars = ax.barh(data['city'], data['total_customer'], color=palette)
    ax.invert_yaxis()
    ax.set_xlabel('Total Pelanggan', fontsize=11)
    ax.set_title(f'Top {top_n_city} Kota dengan Pelanggan Terbanyak', fontweight='bold')
    for bar, val in zip(bars, data['total_customer']):
        ax.text(bar.get_width() + 30, bar.get_y() + bar.get_height()/2,
                f'{val:,}', va='center', fontsize=9)
    plt.tight_layout()
    st.pyplot(fig)

    st.markdown("---")
    st.subheader("📋 Tabel Detail Kota")
    st.dataframe(top_city, use_container_width=True)

# ============================================
# PAGE 5: METODE PEMBAYARAN
# ============================================
elif page == "💳 Metode Pembayaran":
    st.title("💳 Analisis Metode Pembayaran")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Distribusi Metode Pembayaran")
        set_style()
        colors = ['#1a1f36', '#2d6a4f', '#c77dff', '#f4a261']
        fig, ax = plt.subplots(figsize=(8, 7))
        wedges, texts, autotexts = ax.pie(
            top_payment['total'],
            labels=top_payment['payment_type'],
            autopct='%1.1f%%',
            colors=colors,
            startangle=90,
            wedgeprops={'edgecolor': 'white', 'linewidth': 2.5}
        )
        for text in autotexts:
            text.set_fontsize(11)
            text.set_fontweight('bold')
        plt.tight_layout()
        st.pyplot(fig)

    with col2:
        st.subheader("Jumlah Transaksi per Metode")
        set_style()
        fig, ax = plt.subplots(figsize=(8, 6))
        bars = ax.bar(top_payment['payment_type'], top_payment['total'],
                      color=['#1a1f36', '#2d6a4f', '#c77dff', '#f4a261'],
                      edgecolor='white', linewidth=1.5)
        ax.set_xlabel('Metode Pembayaran', fontsize=11)
        ax.set_ylabel('Total Transaksi', fontsize=11)
        for bar, val in zip(bars, top_payment['total']):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 100,
                    f'{val:,}', ha='center', fontsize=9, fontweight='bold')
        plt.tight_layout()
        st.pyplot(fig)

    st.markdown("---")
    st.dataframe(top_payment, use_container_width=True)

# ============================================
# PAGE 6: GEOSPATIAL
# ============================================
elif page == "🗺️ Geospatial Analysis":
    st.title("🗺️ Geospatial Analysis")
    st.markdown("Distribusi pelanggan berdasarkan lokasi geografis di Brazil.")
    st.markdown("---")

    sample_size = st.slider("🔢 Jumlah Sample Titik", 500, 5000, 2000, step=500)
    sample_location = location_df.sample(n=sample_size, random_state=42)

    m = folium.Map(location=[-14.2350, -51.9253], zoom_start=4,
                   tiles='CartoDB positron')

    for _, row in sample_location.iterrows():
        folium.CircleMarker(
            location=[row['geolocation_lat'], row['geolocation_lng']],
            radius=2,
            color='#1a1f36',
            fill=True,
            fill_opacity=0.5
        ).add_to(m)

    st_folium(m, width=1200, height=500)

    st.markdown("---")
    st.subheader("📊 Distribusi Pelanggan per State")
    state_count = location_df['geolocation_state'].value_counts().reset_index()
    state_count.columns = ['state', 'total']

    set_style()
    fig, ax = plt.subplots(figsize=(14, 5))
    palette = sns.color_palette("Blues_r", len(state_count))
    ax.bar(state_count['state'], state_count['total'], color=palette)
    ax.set_xlabel('State', fontsize=11)
    ax.set_ylabel('Total', fontsize=11)
    ax.set_title('Distribusi Pelanggan per State', fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig)

# ============================================
# PAGE 7: CUSTOMER SEGMENTATION
# ============================================
elif page == "👥 Customer Segmentation":
    st.title("👥 Customer Segmentation - RFM Analysis")
    st.markdown("---")

    # Metric cards
    segment_count = rfm_df['Segment'].value_counts().reset_index()
    segment_count.columns = ['Segment', 'Total']

    col1, col2, col3, col4 = st.columns(4)
    segments = ['Champion', 'Loyal Customer', 'At Risk', 'Hibernating']
    icons    = ['👑', '😊', '⚠️', '😴']
    for col, seg, icon in zip([col1, col2, col3, col4], segments, icons):
        val = segment_count[segment_count['Segment'] == seg]['Total'].values
        val = val[0] if len(val) > 0 else 0
        with col:
            st.metric(f"{icon} {seg}", f"{val:,}")

    st.markdown("---")

    # Filter segment
    selected_segment = st.multiselect(
        "🔍 Filter Segment",
        options=rfm_df['Segment'].unique().tolist(),
        default=rfm_df['Segment'].unique().tolist()
    )
    filtered_rfm = rfm_df[rfm_df['Segment'].isin(selected_segment)]

    col1, col2 = st.columns(2)
    palette_seg = {'Champion': '#f4a261', 'Loyal Customer': '#2d6a4f',
                   'At Risk': '#e76f51', 'Hibernating': '#457b9d'}

    with col1:
        st.subheader("Jumlah Customer per Segment")
        data = filtered_rfm['Segment'].value_counts().reset_index()
        data.columns = ['Segment', 'Total']
        set_style()
        fig, ax = plt.subplots(figsize=(8, 5))
        colors = [palette_seg.get(s, '#999') for s in data['Segment']]
        bars = ax.bar(data['Segment'], data['Total'], color=colors,
                      edgecolor='white', linewidth=1.5)
        for bar, val in zip(bars, data['Total']):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 100,
                    f'{val:,}', ha='center', fontsize=9, fontweight='bold')
        ax.set_xlabel('Segment')
        ax.set_ylabel('Jumlah Customer')
        plt.xticks(rotation=15)
        plt.tight_layout()
        st.pyplot(fig)

    with col2:
        st.subheader("Recency vs Monetary")
        set_style()
        fig, ax = plt.subplots(figsize=(8, 5))
        for seg in filtered_rfm['Segment'].unique():
            d = filtered_rfm[filtered_rfm['Segment'] == seg]
            ax.scatter(d['Recency'], d['Monetary'],
                       label=seg, alpha=0.5, s=20,
                       color=palette_seg.get(seg, '#999'))
        ax.set_xlabel('Recency (Hari)')
        ax.set_ylabel('Monetary (R$)')
        ax.legend()
        plt.tight_layout()
        st.pyplot(fig)

    st.markdown("---")
    st.subheader("📊 RFM Summary per Segment")
    rfm_summary = filtered_rfm.groupby('Segment')[['Recency', 'Frequency', 'Monetary']] \
                               .mean().round(2).reset_index()
    st.dataframe(rfm_summary, use_container_width=True)

    st.markdown("---")
    st.subheader("📋 Data RFM Detail")
    st.dataframe(
        filtered_rfm[['customer_unique_id', 'Recency', 'Frequency', 'Monetary', 'Segment']]
        .reset_index(drop=True),
        use_container_width=True
    )

# ============================================
# PAGE 8: CONCLUSION
# ============================================
elif page == "📌 Conclusion":
    st.title("📌 Conclusion & Rekomendasi")
    st.markdown("---")

    st.subheader("📦 Produk")
    st.info("""
    - **bed_bath_table** adalah kategori paling banyak di-order (~11.800 order)
    - **health_beauty** menghasilkan revenue tertinggi (~R$1.27 juta)
    - **watches_gifts** meski di rank ke-7 order, masuk top 2 revenue → harga per item tinggi
    """)

    st.subheader("📈 Tren & Pengiriman")
    st.info("""
    - Order meningkat signifikan di akhir 2017
    - Mayoritas pengiriman **tepat waktu atau lebih cepat** dari estimasi
    - Masih ada sebagian kecil order yang terlambat perlu diperbaiki
    """)

    st.subheader("🏙️ Pelanggan & Pembayaran")
    st.info("""
    - **Sao Paulo** mendominasi sebagai kota pelanggan terbanyak
    - **Credit card** adalah metode pembayaran paling populer
    - Potensi ekspansi besar ke kota-kota tier 2 & 3
    """)

    st.subheader("👥 Customer Segmentation (RFM)")
    st.warning("""
    ⚠️ **94.8% pelanggan tidak aktif** (Hibernating & At Risk)  
    Hanya **4.7% pelanggan aktif** (Loyal Customer + Champion)  
    Bisnis perlu segera strategi reaktivasi pelanggan!
    """)

    st.markdown("---")
    st.subheader("🎯 Rekomendasi Bisnis")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.error("""
        **🔴 Jangka Pendek**
        - Win-back campaign untuk Hibernating
        - Retargeting pelanggan At Risk
        - Promosi health_beauty & watches_gifts
        """)
    with col2:
        st.warning("""
        **🟡 Jangka Menengah**
        - Loyalty program untuk Loyal Customer
        - Ekspansi ke kota tier 2 & 3
        - Kurangi keterlambatan pengiriman
        """)
    with col3:
        st.success("""
        **🟢 Jangka Panjang**
        - VIP treatment untuk Champion
        - Diversifikasi metode pembayaran digital
        - Tingkatkan stok bed_bath_table
        """)

    st.markdown("---")
    st.caption("E-Commerce Dashboard | Dibuat dengan Streamlit 🚀")