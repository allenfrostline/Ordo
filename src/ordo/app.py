from copy import deepcopy
from itertools import combinations

import pandas as pd
import streamlit as st
from st_click_detector import click_detector
from util import INF, fit_exponential_prices, fit_linear_prices, get_b64path

st.set_page_config(layout="centered", page_title="Ordo", page_icon="⚖️")

st.title("⚖️ Ordo")

(tab_intro, tab_usage) = st.tabs(
    [
        "What is Ordo?",
        "Let's start here",
    ]
)

files = None
with tab_intro:
    ordo_definition = """
    **Ordo** is a noun in Latin meaning *a methodical series, arrangement, or order*.
    That is also what this simple web app is going to do: methodically identify your
    preference over a bunch of items that you're having a decidophobia session upon.
    Which ones should you buy? Are you paying too much for the coat? How come these
    two skirts look exactly the same🤯?

    If you're curious (or have been looking at your shopping cart for a few hours),
    feel free to go to the next tab and give it a try. There's nothing to lose except
    some ridiculously priced items from your fuss.
    """
    st.markdown(ordo_definition)


def get_content(b64paths, idx_left, idx_right):
    return """
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        .image-pair {{
            margin-block: 0;
            display: grid;
            grid-template-columns: 1fr 1fr 150px;
        }}
        .image-pair img {{
            object-fit: cover;
            width: 100%;
            height: 100%;
            padding: 10px
        }}
        a#skip {{
            text-decoration: none;
            margin: auto 0;
        }}
        a#skip .skip-hover {{
            visibility: hidden;
            color: white;
            background-color: #9c9c9c;
            border-radius: 5px;
            padding: 1px 4px 3px 5px;
        }}
        a#skip:hover .skip-hover {{
            visibility: visible;
        }}
    </style>
    <div class="image-pair">
        <a href="#" id="{}"><img src="{}"></a>
        <a href="#" id="{}"><img src="{}"></a>
        <a href="#" id="skip">
            <i class="fa-solid fa-forward" style="font-size:20px;color:#9c9c9c;margin-left:5px"></i>
            <span class="skip-hover">skip for now?</span>
        </a>
    </div>
    """.format(
        idx_left,
        b64paths[idx_left],
        idx_right,
        b64paths[idx_right],
    )


pairs = None
with tab_usage:
    if "step1_expanded" not in st.session_state:
        st.session_state["step1_expanded"] = True
    with st.expander(
        label="Step 1: upload your images 🛍️",
        expanded=st.session_state["step1_expanded"],
    ):
        files = (
            st.file_uploader(
                label=(
                    "Please make sure the file names are in the format of "
                    "`{brand_or_item_name}`.`{price}`.`{suffix}` where "
                    "`price` is an integer, and `suffix` is any of common "
                    "image types like `png`, `jpg` etc. "
                    "For example: `nike_airforce.250.png`."
                ),
                accept_multiple_files=True,
            )
            or []
        )
        st.session_state["step1_expanded"] = False
        filenames = []
        files = [
            f for f in files if (filenames := filenames + [f.name]).count(f.name) == 1
        ]
        if files:
            st.success("All images uploaded (you can still add/delete if you want).")

    if files:
        if "known_pairs" not in st.session_state:
            st.session_state["known_pairs"] = set()
            st.session_state["skipped_pairs"] = set()
            st.session_state["better_than"] = dict()

        b64paths = [get_b64path(f.getvalue()) for f in files]
        titles = []
        prices = []
        for f in files:
            title, price, _ = f.name.split(".", 2)
            titles.append(title)
            prices.append(int(price))
        pairs = list(combinations(range(len(files)), 2))
        pairs = [
            p
            for p in pairs
            if (p not in st.session_state["known_pairs"])
            and (p[::-1] not in st.session_state["known_pairs"])
        ]
        skipped_pairs = [p for p in pairs if p in st.session_state["skipped_pairs"]]
        not_skipped_pairs = [p for p in pairs if p not in skipped_pairs]
        pairs = not_skipped_pairs + skipped_pairs
        st.session_state["step2_expanded"] = bool(pairs)
        st.session_state["step3_expanded"] = False

        with st.expander(
            label="Step 2: choose between the two 🤯",
            expanded=st.session_state["step2_expanded"],
        ):
            if pairs:
                st.markdown("Click on the image that you prefer:")
                st.session_state["curr_pair"] = pairs.pop(0)
                clicked = click_detector(
                    get_content(b64paths, *st.session_state["curr_pair"])
                )
                st.markdown(f"Remaining comparisons (at most) after this: {len(pairs)}")

                if clicked != "":
                    if clicked == "skip":
                        if (
                            st.session_state["curr_pair"]
                            not in st.session_state["skipped_pairs"]
                        ):
                            st.session_state["skipped_pairs"].add(
                                st.session_state["curr_pair"]
                            )
                            st.rerun()
                    else:
                        idx_better = int(clicked)
                        idx_worse = (
                            st.session_state["curr_pair"][0]
                            ^ st.session_state["curr_pair"][1]
                            ^ idx_better
                        )
                        print(f"{idx_better} > {idx_worse}")
                        better_than = deepcopy(st.session_state["better_than"])
                        if idx_better not in better_than:
                            better_than[idx_better] = set()
                        idx_worse_extended = {idx_worse} | better_than.get(
                            idx_worse, set()
                        )
                        better_than[idx_better] |= idx_worse_extended
                        st.session_state["known_pairs"] |= {
                            (idx_better, i) for i in idx_worse_extended
                        }
                        for k, v in better_than.items():
                            if idx_better in v:
                                better_than[k] |= idx_worse_extended
                        st.session_state["better_than"] = better_than
                        st.rerun()
            else:
                better_than = sorted(
                    st.session_state["better_than"],
                    key=lambda k: len(st.session_state["better_than"][k]),
                    reverse=True,
                )
                idx_last = [i for i in range(len(files)) if i not in better_than]
                better_than += idx_last
                assert len(better_than) == len(files)
                better_than_html = """
                <style>
                    .image-chain {{
                        margin-block: 0;
                        display: grid;
                        grid-template-columns: repeat({}, auto);
                    }}
                    .image-chain img {{
                        object-fit: cover;
                        width: 100%;
                        height: 100%;
                        padding: 5px;
                    }}
                </style>
                <div class="image-chain">{}</div>         
                """.format(
                    len(better_than),
                    "".join([f'<img src="{b64paths[i]}">' for i in better_than]),
                )
                st.markdown(better_than_html, unsafe_allow_html=True)
                st.success(
                    "All images ranked above, with the first being your favorite."
                )

                st.session_state["step3_expanded"] = True

        if st.session_state["step3_expanded"]:
            with st.expander(
                label="Step 3: calibrate your price curve 📈",
                expanded=st.session_state["step3_expanded"],
            ):
                dist_type = st.radio(
                    label="Select a distribution:",
                    options=["Linear", "Exponential"],
                    captions=[
                        '"Everything is similar to everything in this pool"',
                        '"I think there is a long and expensive right tail"',
                    ],
                    horizontal=True,
                    label_visibility="collapsed",
                )
                values = None
                if dist_type == "Linear":
                    col1, col2 = st.columns(2)
                    with col1:
                        price1 = st.number_input(
                            "What would you pay for the piece below?",
                            step=1,
                            value=None,
                            min_value=0,
                            key="price_left",
                        )
                        st.markdown(
                            '<img src="{}" width=100%>'.format(
                                b64paths[better_than[0]]
                            ),
                            unsafe_allow_html=True,
                        )
                    with col2:
                        price2 = st.number_input(
                            "What would you pay for the piece below?",
                            step=1,
                            value=None,
                            min_value=0,
                            key="price_right",
                        )
                        st.markdown(
                            '<img src="{}" width=100%>'.format(
                                b64paths[better_than[-1]]
                            ),
                            unsafe_allow_html=True,
                        )
                    if None not in (price1, price2):
                        if not (price1 > price2):
                            st.error(
                                "The prices must be in descending order due to your preference in step 2."
                                "Please re-enter your pricing."
                            )
                        else:
                            values = fit_linear_prices(price1, price2, len(better_than))
                elif dist_type == "Exponential":
                    n = len(better_than)
                    if n < 3:
                        st.error(
                            f"Cannot fit exponential curve with only n={n} pieces. Please choose linear instead."
                        )
                        st.stop()
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        price1 = st.number_input(
                            "What would you pay for the piece below?",
                            step=1,
                            value=None,
                            min_value=0,
                            key="price_left",
                        )
                        st.markdown(
                            '<img src="{}" width=100%>'.format(
                                b64paths[better_than[0]]
                            ),
                            unsafe_allow_html=True,
                        )
                    with col2:
                        price2 = st.number_input(
                            "What would you pay for the piece below?",
                            step=1,
                            value=None,
                            min_value=0,
                            key="price_mid",
                        )
                        st.markdown(
                            '<img src="{}" width=100%>'.format(
                                b64paths[better_than[n // 2]]
                            ),
                            unsafe_allow_html=True,
                        )
                    with col3:
                        price3 = st.number_input(
                            "What would you pay for the piece below?",
                            step=1,
                            value=None,
                            min_value=0,
                            key="price_right",
                        )
                        st.markdown(
                            '<img src="{}" width=100%>'.format(
                                b64paths[better_than[-1]]
                            ),
                            unsafe_allow_html=True,
                        )
                    if None not in (price1, price2, price3):
                        if not (price1 > price2 > price3):
                            st.error(
                                "The prices must be in descending order due to your preference in step 2."
                                "Please re-enter your pricing."
                            )
                        else:
                            values = fit_exponential_prices(price1, price2, price3, n)

                else:
                    raise ValueError

                if values is not None:
                    assert len(titles) == len(better_than)
                    df_summary = pd.DataFrame(
                        {
                            "name": [titles[i] for i in better_than],
                            "price": [prices[i] for i in better_than],
                            "value": values,
                            "preview": [b64paths[i] for i in better_than],
                        }
                    )
                    df_summary["price - value"] = df_summary.eval("price - value")
                    df_summary.index.name = "preference"
                    vm = df_summary["price - value"].abs().max()
                    st.success(
                        "🎉Congratulations!"
                        "All steps are finished and your final summary table is now shown below:"
                    )
                    if "limit" not in st.session_state:
                        st.session_state["limit"] = None
                    st.dataframe(
                        df_summary[
                            df_summary["price - value"]
                            <= (st.session_state["limit"] or INF)
                        ]
                        .reset_index()
                        .style.format(precision=0)
                        .background_gradient(
                            cmap="RdYlGn_r",
                            subset="price - value",
                            low=0.1,
                            high=0.1,
                            vmin=-vm,
                            vmax=vm,
                        ),
                        column_config={
                            "preference": st.column_config.Column(
                                "❤️ Your Preference", help="Smaller means better!"
                            ),
                            "name": st.column_config.Column("👔 Name"),
                            "price": st.column_config.Column("💰 Listed Price"),
                            "value": st.column_config.Column("✒️ Your Estimate"),
                            "preview": st.column_config.ImageColumn(
                                "🖼️ Preview",
                                help="Double click or press `SPACE` to preview larger image",
                            ),
                            "price - value": st.column_config.Column(
                                "🔥 Price - Estimate", help="Lower means better!"
                            ),
                        },
                        use_container_width=True,
                        hide_index=True,
                    )
                    limit = st.number_input(
                        "If you want, you can **ignore** all items with price - value **above** certain value:",
                        step=1,
                        value=None,
                        key="limit-input",
                    )
                    if limit != st.session_state["limit"]:
                        st.session_state["limit"] = limit
                        st.rerun()
