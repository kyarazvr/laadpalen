import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import streamlit as st
import plotly.figure_factory as ff

#--------------------------------------------------------
#laadpalendata
#--------------------------------------------------------
df = pd.read_csv('laadpaaldata.csv')
df.head()

df.info()

#datum 2018-02-29 omzetten naar NaT, 2018 geen schrikkeljaar. 
df['Started'] = pd.to_datetime(df['Started'], errors='coerce')
df['Ended'] = pd.to_datetime(df['Ended'], errors='coerce')


#'Started' en 'Ended' naar datetime omzetten
df['Started'] = pd.to_datetime(df['Started'])
df['Ended'] = pd.to_datetime(df['Ended'])

#Extra kollom maken voor het uur van de dag
df['HourOfDay'] = df['Started'].dt.hour

#Verwijder rijen met negatieve waarden
df = df[df['ChargeTime'] >= 0]

df['Weekday'] = df['Started'].dt.day_name()

df['Weekday'].describe()

df['TotalEnergy (kwh)'] = df['TotalEnergy'] / 1000
df.head()

#de snelheid wordt berekend door de totale energie te delen door de oplaadtijd.
df['ChargeSpeed'] =  df['TotalEnergy (kwh)'] / df['ChargeTime'] 

# niet opgeladen tijd kijken
df['NotChargeTime'] = df['ConnectedTime'] - df['ChargeTime']

#----------------------------------------------------------------
#streamlit app maken 
#----------------------------------------------------------------
page = st.sidebar.selectbox("Select a Page",['Laadpalen', "Map", 'Info auto'])

if page == 'Laadpalen':
    st.title('Laadpalen dataonderzoek')
    st.write("Op deze pagina wordt onderzoek gedaan naar de relaties tussen de oplaadtijden, oplaadsnelheden en de maximale oplaadvermogen van auto's")
    
    tab1, tab2,tab3,tab4 = st.tabs(["Oplaadtijd vs uur per dag", "Niet-opgeladen tijd vs uur per dag", "Oplaad snelheid vs Maximale vermogen", "voorbeeld"])
    with tab1:
        st.title("Onderzoek naar laadpalen")
        st.subheader("kansdichthied tussen de oplaadtijd per uur van de dag")
        st.write("Door een lijngrafiek te maken kunnen we de relatie zien tussen de snelheid van opladen in kwh per uur van een dag (24 uur)")


        df1 = df[df['ChargeTime'] <= 24]

        # Assuming df is your DataFrame and 'ChargeTime' is the column of interest
        charge_times = df1['ChargeTime']

        #Create KDE plot for ChargeTime
        fig4 = ff.create_distplot([charge_times], ['ChargeTime'], colors=['blue'])

        # Calculate mean and median
        mean_charge_time = charge_times.mean()
        median_charge_time = charge_times.median()

        # Add vertical lines for mean and median
        fig4.add_vline(x=mean_charge_time, line_dash="dash", line_color="red", annotation_text=f'Mean: {mean_charge_time:.2f} hours', annotation_position="top right")
        fig4.add_vline(x=median_charge_time, line_dash="dash", line_color="green", annotation_text=f'Median: {median_charge_time:.2f} hours', annotation_position="bottom right")

        # Update layout
        fig4.update_layout(
            title='Histogram of Charging Time',
            xaxis_title='Charging Time (hours)',
            yaxis_title='Count'
        )
        # Show the plot
        st.plotly_chart(fig4)

        st.subheader("Voor weekday")    

            # Group data by 'Weekday' and get 'ChargeTime' for each group
        hist_data = []
        group_labels = []

        for day in df['Weekday'].unique():
            charge_times_day = df[df['Weekday'] == day]['ChargeTime']
            if not charge_times_day.empty:
                hist_data.append(charge_times_day)
                group_labels.append(day)

        # Create distplots for each weekday if there's data
        if hist_data:
            fig = ff.create_distplot(hist_data, group_labels, bin_size=0.5, show_hist=False)

            # Update layout
            fig.update_layout(
                title='Distribution of Charging Time by Weekday',
                xaxis_title='Charging Time (hours)',
                yaxis_title='Density'
            )

            # Display the plot
            st.plotly_chart(fig)
        else:
            print('No data available to create distplots.')

       
    with tab2:
        fig2 = px.scatter(df, x='MaxPower', y='ChargeSpeed', color='Weekday',
                 title='Charge Speed vs Max Power with Trendline by Weekday')
        st.plotly_chart(fig2)
    
    with tab3:
        fig3 = sns.relplot(kind= 'line', data= df, x= 'HourOfDay', y= 'NotChargeTime', hue= 'Weekday', col= 'Weekday', errorbar = None)
        st.pyplot(fig3)
        st.text("sup")
    







