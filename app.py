"""Project Crumb — demo bakery operations dashboard built with Streamlit."""
import sqlite3
from datetime import date, timedelta
import streamlit as st
from database import (initialize, create_request, get_requests, update_status,
                      set_archived, get_inventory, add_inventory, adjust_inventory,
                      delete_inventory, seed_demo)

st.set_page_config(page_title='Project Crumb', page_icon='🧁', layout='wide')
initialize()

st.markdown('''<style>
.stApp {background-color:#fffaf7;}
h1,h2,h3 {color:#663c49;}
[data-testid="stMetric"] {background:#fff0ed; padding:16px; border-radius:14px;}
.stButton>button[kind="primary"] {background:#a04d6a; border-color:#a04d6a;}
</style>''', unsafe_allow_html=True)

st.sidebar.title('🧁 Project Crumb')
st.sidebar.caption('Bakery Operations Dashboard')
role = st.sidebar.selectbox('Demo role', ['Employee', 'Baker', 'Owner'])
page = st.sidebar.radio('Navigate', ['Dashboard', 'Cake Requests', 'Inventory'])
st.sidebar.divider()
st.sidebar.caption('Portfolio demo: role switcher is not login/authentication. Do not enter real customer data.')
if st.sidebar.button('Load fictional demo data', help='Adds samples only if the corresponding tables are empty'):
    seed_demo()
    st.rerun()

requests = get_requests()
items = get_inventory()
active = [r for r in requests if not r['archived']]
low_stock = [i for i in items if i['quantity'] <= i['low_stock_at']]

if page == 'Dashboard':
    st.title('Bakery Dashboard')
    st.caption('A simple place to manage custom cakes and stock.')
    a,b,c,d = st.columns(4)
    a.metric('Active requests', len(active))
    b.metric('Pending approvals', sum(r['status']=='Pending' for r in active))
    c.metric('Approved cakes', sum(r['status']=='Approved' for r in active))
    d.metric('Low-stock items', len(low_stock))
    st.subheader('Upcoming pickups')
    upcoming = [r for r in active if r['pickup_date'] >= date.today().isoformat()]
    if upcoming:
        st.dataframe([{'#':r['id'], 'Customer':r['customer_name'], 'Pickup':r['pickup_date'], 'Status':r['status']}
                      for r in upcoming[:15]], use_container_width=True, hide_index=True)
    else:
        st.info('No upcoming pickups yet. Create a cake request or load fictional demo data.')
    if low_stock:
        st.warning('Low stock: ' + ', '.join(i['name'] for i in low_stock))

elif page == 'Cake Requests':
    st.title('Custom Cake Requests')
    if role in ('Employee', 'Owner'):
        with st.expander('➕ New cake request', expanded=not requests):
            with st.form('new_cake', clear_on_submit=True):
                c1,c2 = st.columns(2)
                customer = c1.text_input('Customer name *')
                phone = c2.text_input('Phone (optional)')
                size = c1.selectbox('Cake size', ['6 inch','8 inch','10 inch','Quarter sheet','Half sheet'])
                flavor = c2.selectbox('Cake flavor', ['Vanilla','Chocolate','Red velvet','Funfetti','Strawberry','Other'])
                frosting = c1.selectbox('Frosting', ['Vanilla buttercream','Chocolate buttercream','Cream cheese','Other'])
                pickup = c2.date_input('Pickup date', min_value=date.today(), value=date.today()+timedelta(days=3))
                decorations = st.text_input('Decorations / message')
                instructions = st.text_area('Special instructions')
                if st.form_submit_button('Save request', type='primary'):
                    if not customer.strip():
                        st.error('Please enter a customer name.')
                    else:
                        create_request(customer, phone, size, flavor, frosting, decorations, pickup, instructions)
                        st.success('Cake request saved!')
                        st.rerun()
    else:
        st.caption('Bakers review and update submitted requests.')

    c1,c2,c3 = st.columns([2,1,1])
    search = c1.text_input('Search customer or request ID', placeholder='Search…')
    status_filter = c2.selectbox('Status', ['All','Pending','Approved','Changes Requested','Declined','Completed'])
    view = c3.selectbox('View', ['Active','Archived'])
    filtered = [r for r in requests if r['archived'] == (view=='Archived')
                and (status_filter=='All' or r['status']==status_filter)
                and (search.lower() in r['customer_name'].lower() or search.strip()==str(r['id']))]
    st.caption(f'{len(filtered)} request(s) found')
    if not filtered:
        st.info('No matching cake requests.')
    for r in filtered:
        with st.expander(f"#{r['id']} · {r['customer_name']} · {r['pickup_date']} · {r['status']}"):
            left,right=st.columns([2,1])
            left.write(f"**Cake:** {r['size']} {r['cake_flavor']} · {r['frosting']}")
            left.write(f"**Decorations:** {r['decorations'] or 'None'}")
            left.write(f"**Instructions:** {r['instructions'] or 'None'}")
            left.write(f"**Phone:** {r['phone'] or 'Not provided'}")
            if r['baker_note']:
                left.info(f"Baker note: {r['baker_note']}")
            if role in ('Baker','Owner') and not r['archived']:
                new_status = right.selectbox('Decision', ['Pending','Approved','Changes Requested','Declined','Completed'],
                                             index=['Pending','Approved','Changes Requested','Declined','Completed'].index(r['status']), key=f's_{r["id"]}')
                note = right.text_area('Baker note', value=r['baker_note'],key=f'n_{r["id"]}')
                if right.button('Save decision', key=f'update_{r["id"]}', type='primary'):
                    update_status(r['id'], new_status, note)
                    st.rerun()
            if role == 'Owner':
                label = 'Restore request' if r['archived'] else 'Archive request'
                if st.button(label, key=f'archive_{r["id"]}'):
                    set_archived(r['id'], not r['archived'])
                    st.rerun()

elif page == 'Inventory':
    st.title('Inventory')
    if role != 'Owner':
        st.caption('Read-only stock view. Owner role can manage inventory.')
    else:
        with st.expander('➕ Add inventory item'):
            with st.form('new_inventory', clear_on_submit=True):
                n,c = st.columns(2)
                name = n.text_input('Item name *')
                category = c.selectbox('Category', ['Dry ingredients','Dairy','Decorations & flavoring','Packaging','Other'])
                qty = n.number_input('Starting quantity', min_value=0, value=0, step=1)
                threshold = c.number_input('Low-stock alert at or below', min_value=0, value=5, step=1)
                unit = st.text_input('Unit (e.g., bags, boxes, lbs)', value='units')
                if st.form_submit_button('Add item', type='primary'):
                    if not name.strip() or not unit.strip():
                        st.error('Item name and unit are required.')
                    else:
                        try:
                            add_inventory(name,category,qty,threshold,unit)
                            st.rerun()
                        except sqlite3.IntegrityError:
                            st.error('That item already exists.')
    if not items:
        st.info('Inventory is empty. Use the owner role to add an item or load fictional demo data.')
    categories=sorted(set(i['category'] for i in items))
    for category in categories:
        category_items=[i for i in items if i['category']==category]
        warnings=sum(i['quantity']<=i['low_stock_at'] for i in category_items)
        with st.expander(f'{category} · {len(category_items)} items' + (f' · ⚠️ {warnings} low' if warnings else ''), expanded=True):
            for i in category_items:
                a,b,c,d,e=st.columns([3,2,1,1,1])
                a.write(f"**{i['name']}**" + ('  ⚠️ Low' if i['quantity']<=i['low_stock_at'] else ''))
                b.write(f"{i['quantity']} {i['unit']} (alert ≤ {i['low_stock_at']})")
                if role == 'Owner':
                    if c.button('− 1', key=f'minus_{i["id"]}'):
                        if not adjust_inventory(i['id'],-1):
                            st.warning('Quantity cannot be negative.')
                        else:
                            st.rerun()
                    if d.button('+ 1', key=f'plus_{i["id"]}'):
                        adjust_inventory(i['id'],1)
                        st.rerun()
                    if e.button('Delete', key=f'delete_{i["id"]}'):
                        delete_inventory(i['id'])
                        st.rerun()
                st.divider()
