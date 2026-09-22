from backend import (
    chatbot,
    get_all_threads,
    ingest_rag_document
)

from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    ToolMessage
)

from langgraph.types import Command

import streamlit as st
import tempfile
import os
import uuid


# =========================================================
# THREAD FUNCTIONS
# =========================================================

def generate_thread_id():

    return str(uuid.uuid4())


def add_thread(thread_id):

    if thread_id not in st.session_state["chat_threads"]:

        st.session_state["chat_threads"].append(
            thread_id
        )


def reset_chat():

    st.session_state["thread_id"] = (
        generate_thread_id()
    )

    st.session_state["message_history"] = []

    st.session_state["hitl_pending"] = False

    st.session_state["hitl_message"] = None


# =========================================================
# CONFIG
# =========================================================

def get_config():

    return {
        "configurable": {
            "thread_id":
                st.session_state["thread_id"]
        },

        "metadata": {
            "thread_id":
                st.session_state["thread_id"]
        },

        "run_name": "chat_trace"
    }


# =========================================================
# LOAD CONVERSATION
# =========================================================

def load_conversation(thread_id):

    state = chatbot.get_state(
        config={
            "configurable": {
                "thread_id": thread_id
            }
        }
    )

    return state.values.get(
        "messages",
        []
    )


# =========================================================
# CONTENT HELPER
# =========================================================

def extract_text(content):

    if isinstance(content, str):

        return content


    if isinstance(content, list):

        text_parts = []

        for part in content:

            if isinstance(part, str):

                text_parts.append(part)

            elif (
                isinstance(part, dict)
                and "text" in part
            ):

                text_parts.append(
                    part["text"]
                )

        return "".join(text_parts)


    return str(content)


# =========================================================
# GET LATEST AI MESSAGE
# =========================================================

def get_latest_ai_message(messages):

    for message in reversed(messages):

        if isinstance(
            message,
            AIMessage
        ):

            content = extract_text(
                message.content
            )

            if content:

                return content

    return None


# =========================================================
# INITIALIZE SESSION STATE
# =========================================================

if "message_history" not in st.session_state:

    st.session_state["message_history"] = []


if "thread_id" not in st.session_state:

    st.session_state["thread_id"] = (
        generate_thread_id()
    )


if "chat_threads" not in st.session_state:

    st.session_state["chat_threads"] = (
        get_all_threads()
    )


if "hitl_pending" not in st.session_state:

    st.session_state["hitl_pending"] = False


if "hitl_message" not in st.session_state:

    st.session_state["hitl_message"] = None


# =========================================================
# PAGE
# =========================================================

st.title(
    "Agentic Chatbot with LangGraph"
)


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title(
    "My Conversations"
)


# =========================================================
# NEW CHAT
# =========================================================

if st.sidebar.button(
    "New Chat",
    use_container_width=True
):

    reset_chat()

    st.rerun()


# =========================================================
# EXISTING THREADS
# =========================================================

for thread_id in (
    st.session_state["chat_threads"][::-1]
):

    if st.sidebar.button(
        str(thread_id),
        key=f"thread_{thread_id}",
        use_container_width=True
    ):

        st.session_state["thread_id"] = (
            thread_id
        )

        messages = load_conversation(
            thread_id
        )

        temp_messages = []


        for message in messages:

            if isinstance(
                message,
                HumanMessage
            ):

                role = "user"

            elif isinstance(
                message,
                AIMessage
            ):

                role = "assistant"

            else:

                continue


            content = extract_text(
                message.content
            )


            if not content:

                continue


            temp_messages.append(
                {
                    "role": role,
                    "content": content
                }
            )


        st.session_state[
            "message_history"
        ] = temp_messages


        # Clear HITL state
        st.session_state[
            "hitl_pending"
        ] = False

        st.session_state[
            "hitl_message"
        ] = None


        st.rerun()


# =========================================================
# DISPLAY CHAT HISTORY
# =========================================================

for message in (
    st.session_state["message_history"]
):

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# =========================================================
# HITL APPROVAL UI
# =========================================================

if st.session_state["hitl_pending"]:

    st.warning(
        "⚠️ Human approval is required "
        "before this action can continue."
    )


    st.info(
        "🤖 **Agent is requesting approval:**\n\n"
        + str(
            st.session_state["hitl_message"]
        )
    )


    col1, col2 = st.columns(2)


    # =====================================================
    # APPROVE
    # =====================================================

    with col1:

        if st.button(
            "✅ Approve",
            use_container_width=True
        ):

            CONFIG = get_config()


            # ---------------------------------------------
            # Get current checkpoint
            # ---------------------------------------------

            current_state = (
                chatbot.get_state(
                    CONFIG
                )
            )


            old_messages = (
                current_state.values.get(
                    "messages",
                    []
                )
            )


            old_message_count = (
                len(old_messages)
            )


            # ---------------------------------------------
            # Resume graph
            # ---------------------------------------------

            with st.spinner(
                "Processing approval..."
            ):

                result = chatbot.invoke(
                    Command(
                        resume="yes"
                    ),
                    config=CONFIG
                )


            # ---------------------------------------------
            # Check another interrupt
            # ---------------------------------------------

            interrupts = result.get(
                "__interrupt__",
                []
            )


            if interrupts:

                st.session_state[
                    "hitl_pending"
                ] = True

                st.session_state[
                    "hitl_message"
                ] = interrupts[0].value

                st.rerun()


            # ---------------------------------------------
            # Only new messages
            # ---------------------------------------------

            new_messages = (
                result.get(
                    "messages",
                    []
                )[old_message_count:]
            )


            # ---------------------------------------------
            # Get final AI response
            # ---------------------------------------------

            ai_message = (
                get_latest_ai_message(
                    new_messages
                )
            )


            if ai_message:

                st.session_state[
                    "message_history"
                ].append(
                    {
                        "role": "assistant",
                        "content": ai_message
                    }
                )


            # Clear HITL
            st.session_state[
                "hitl_pending"
            ] = False

            st.session_state[
                "hitl_message"
            ] = None


            st.rerun()


    # =====================================================
    # REJECT
    # =====================================================

    with col2:

        if st.button(
            "❌ Reject",
            use_container_width=True
        ):

            CONFIG = get_config()


            # ---------------------------------------------
            # Get current checkpoint
            # ---------------------------------------------

            current_state = (
                chatbot.get_state(
                    CONFIG
                )
            )


            old_messages = (
                current_state.values.get(
                    "messages",
                    []
                )
            )


            old_message_count = (
                len(old_messages)
            )


            # ---------------------------------------------
            # Resume with rejection
            # ---------------------------------------------

            with st.spinner(
                "Processing rejection..."
            ):

                result = chatbot.invoke(
                    Command(
                        resume="no"
                    ),
                    config=CONFIG
                )


            # ---------------------------------------------
            # Check another interrupt
            # ---------------------------------------------

            interrupts = result.get(
                "__interrupt__",
                []
            )


            if interrupts:

                st.session_state[
                    "hitl_pending"
                ] = True

                st.session_state[
                    "hitl_message"
                ] = interrupts[0].value

                st.rerun()


            # ---------------------------------------------
            # Only new messages
            # ---------------------------------------------

            new_messages = (
                result.get(
                    "messages",
                    []
                )[old_message_count:]
            )


            # ---------------------------------------------
            # Get final AI response
            # ---------------------------------------------

            ai_message = (
                get_latest_ai_message(
                    new_messages
                )
            )


            if ai_message:

                st.session_state[
                    "message_history"
                ].append(
                    {
                        "role": "assistant",
                        "content": ai_message
                    }
                )


            # Clear HITL
            st.session_state[
                "hitl_pending"
            ] = False

            st.session_state[
                "hitl_message"
            ] = None


            st.rerun()


# =========================================================
# CHAT INPUT
# =========================================================

# Don't allow another question while approval
# is waiting.

if not st.session_state["hitl_pending"]:

    chat_input = st.chat_input(
        "Type here",
        accept_file=True,
        file_type=["pdf"]
    )


    user_input = (
        chat_input.text
        if chat_input
        else None
    )


    uploaded_file = (
        chat_input.files[0]
        if (
            chat_input
            and chat_input.files
        )
        else None
    )


    # =====================================================
    # PDF UPLOAD
    # =====================================================

    if uploaded_file is not None:

        if (
            st.session_state.get(
                "processed_file_name"
            )
            != uploaded_file.name
        ):

            with st.spinner(
                "Processing PDF..."
            ):

                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".pdf"
                ) as tmp_file:

                    tmp_file.write(
                        uploaded_file.getvalue()
                    )

                    tmp_path = tmp_file.name


                ingest_rag_document(
                    tmp_path
                )


                os.remove(
                    tmp_path
                )


                st.session_state[
                    "processed_file_name"
                ] = uploaded_file.name


    # =====================================================
    # PROCESS USER MESSAGE
    # =====================================================

    if (
        user_input
        or uploaded_file is not None
    ):

        # -----------------------------------------------
        # Add thread
        # -----------------------------------------------

        add_thread(
            st.session_state[
                "thread_id"
            ]
        )


        # -----------------------------------------------
        # Display user message
        # -----------------------------------------------

        display_text = (
            user_input or ""
        )


        if uploaded_file is not None:

            display_text = (
                f"📎 {uploaded_file.name}\n\n"
                f"{display_text}"
            ).strip()


        st.session_state[
            "message_history"
        ].append(
            {
                "role": "user",
                "content": display_text
            }
        )


        with st.chat_message("user"):

            st.markdown(
                display_text
            )


        # -----------------------------------------------
        # Message sent to LLM
        # -----------------------------------------------

        llm_message = (
            user_input or ""
        )


        if uploaded_file is not None:

            note = (
                f"[The user just uploaded a "
                f"document named "
                f"'{uploaded_file.name}'. "
                f"Use the rag_tool to answer "
                f"questions related to this document.]\n\n"
            )

            llm_message = (
                note
                + (
                    user_input
                    or
                    "Please confirm the document "
                    "was received."
                )
            )


        # =================================================
        # CONFIG
        # =================================================

        CONFIG = get_config()


        # =================================================
        # GET CHECKPOINT BEFORE THIS TURN
        # =================================================

        current_state = (
            chatbot.get_state(
                CONFIG
            )
        )


        old_messages = (
            current_state.values.get(
                "messages",
                []
            )
        )


        old_message_count = (
            len(old_messages)
        )


        # =================================================
        # RUN GRAPH
        # =================================================

        with st.chat_message(
            "assistant"
        ):

            tool_placeholder = (
                st.empty()
            )


            text_placeholder = (
                st.empty()
            )


            # ---------------------------------------------
            # Invoke graph
            # ---------------------------------------------

            result = chatbot.invoke(

                {
                    "messages": [
                        HumanMessage(
                            content=llm_message
                        )
                    ]
                },

                config=CONFIG
            )


            # =================================================
            # CHECK HITL INTERRUPT
            # =================================================

            interrupts = result.get(
                "__interrupt__",
                []
            )


            # ---------------------------------------------
            # HITL detected
            # ---------------------------------------------

            if interrupts:

                # -----------------------------------------
                # Process tool call before interrupt
                # -----------------------------------------

                new_messages = (
                    result.get(
                        "messages",
                        []
                    )[old_message_count:]
                )


                for message in new_messages:

                    if (
                        isinstance(
                            message,
                            AIMessage
                        )
                        and message.tool_calls
                    ):

                        for tc in (
                            message.tool_calls
                        ):

                            tool_name = tc.get(
                                "name"
                            )

                            tool_args = tc.get(
                                "args"
                            )


                            if tool_name:

                                tool_placeholder.info(
                                    f"🔧 Calling tool: "
                                    f"**{tool_name}**\n\n"
                                    f"Arguments: "
                                    f"`{tool_args}`"
                                )


                # -----------------------------------------
                # Save HITL state
                # -----------------------------------------

                prompt_to_human = (
                    interrupts[0].value
                )


                st.session_state[
                    "hitl_pending"
                ] = True


                st.session_state[
                    "hitl_message"
                ] = prompt_to_human


                # -----------------------------------------
                # Display approval message
                # -----------------------------------------

                st.warning(
                    "⚠️ **Human approval required**\n\n"
                    + str(
                        prompt_to_human
                    )
                )


                # -----------------------------------------
                # Rerun Streamlit
                # -----------------------------------------

                st.rerun()


            # =================================================
            # NORMAL RESPONSE
            # =================================================

            new_messages = (
                result.get(
                    "messages",
                    []
                )[old_message_count:]
            )


            # ---------------------------------------------
            # Display tools
            # ---------------------------------------------

            tool_calls_seen = set()


            for message in new_messages:

                # -----------------------------------------
                # AI tool call
                # -----------------------------------------

                if (
                    isinstance(
                        message,
                        AIMessage
                    )
                    and message.tool_calls
                ):

                    for tc in (
                        message.tool_calls
                    ):

                        tool_name = tc.get(
                            "name"
                        )

                        tool_args = tc.get(
                            "args"
                        )


                        if (
                            tool_name
                            and tool_name
                            not in tool_calls_seen
                        ):

                            tool_calls_seen.add(
                                tool_name
                            )


                            tool_placeholder.info(
                                f"🔧 Calling tool: "
                                f"**{tool_name}**\n\n"
                                f"Arguments: "
                                f"`{tool_args}`"
                            )


                # -----------------------------------------
                # Tool result
                # -----------------------------------------

                elif isinstance(
                    message,
                    ToolMessage
                ):

                    tool_placeholder.success(
                        f"✅ **{message.name}** "
                        f"returned a result"
                    )


            # ---------------------------------------------
            # Final AI response
            # ---------------------------------------------

            ai_message = (
                get_latest_ai_message(
                    new_messages
                )
            )


            if ai_message:

                text_placeholder.markdown(
                    ai_message
                )


                st.session_state[
                    "message_history"
                ].append(
                    {
                        "role": "assistant",
                        "content": ai_message
                    }
                )